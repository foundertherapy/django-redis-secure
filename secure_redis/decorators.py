from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from functools import wraps
from collections import defaultdict
import logging
import datetime

from django.conf import settings as global_settings
import rq.utils
from rq.compat import string_types
import django_rq
from django_rq.queues import get_queue
from rq.defaults import DEFAULT_RESULT_TTL
from rq.queue import Queue
from . import settings

logger = logging.getLogger(__name__)


_serializer = None


def get_serializer():
    global _serializer
    if not _serializer:
        from . import serializer
        _serializer = serializer.SecureSerializer(settings.get_secure_cache_opts())
    return _serializer


def execute(method_name, *args, **kwargs):
    return rq.utils.import_attribute(method_name)(*args, **kwargs)


def secure_job_proxy(*args, **kwargs):
    args2 = list(args)
    f_name = get_serializer().loads(args2.pop(0))
    args = list(get_serializer().loads(args2.pop(0)))
    kwargs = get_serializer().loads(args2.pop())
    return execute(f_name, *args, **kwargs)


def rq_job(func_or_queue, connection=None, *args, **kwargs):
    class _rq_job(object):
        def __init__(self, queue, connection=None, timeout=None,
                     result_ttl=DEFAULT_RESULT_TTL, ttl=None):
            """A decorator that adds a ``delay`` method to the decorated function,
            which in turn creates a RQ job when called. Accepts a required
            ``queue`` argument that can be either a ``Queue`` instance or a string
            denoting the queue name.  For example:

                @job(queue='default')
                def simple_add(x, y):
                    return x + y

                simple_add.delay(1, 2) # Puts simple_add function into queue
            """
            self.queue = queue
            self.connection = connection
            self.timeout = timeout
            self.result_ttl = result_ttl
            self.ttl = ttl

        def __call__(self, f):
            @wraps(f)
            def delay(*args, **kwargs):
                if isinstance(self.queue, string_types):
                    queue = Queue(name=self.queue, connection=self.connection)
                else:
                    queue = self.queue
                depends_on = kwargs.pop('depends_on', None)
                f_name = '{}.{}'.format(func_or_queue.__module__, func_or_queue.__name__)
                args2 = [get_serializer().dumps(f_name)]
                args2 += [get_serializer().dumps(args)]

                args2 += [get_serializer().dumps(kwargs)]
                return queue.enqueue_call(secure_job_proxy, args=args2, kwargs={},
                                          timeout=self.timeout, result_ttl=self.result_ttl,
                                          ttl=self.ttl, depends_on=depends_on)

            @wraps(f)
            def enqueue_at(target_date, scheduler_name='default', *args, **kwargs):
                f_name = '{0}.{1}'.format(func_or_queue.__module__, func_or_queue.__name__)
                args2 = [get_serializer().dumps(f_name)]
                args2 += [get_serializer().dumps(args)]

                args2 += [get_serializer().dumps(kwargs)]

                scheduler = django_rq.get_scheduler(scheduler_name)
                proxy_method_name = '{}.{}'.format(secure_job_proxy.__module__, secure_job_proxy.__name__)
                return scheduler.enqueue_at(target_date, proxy_method_name, *args2, **{})

            @wraps(f)
            def schedule_once(interval, timeout=None):
                """
                Schedule job once or reschedule when interval changes
                """
                rq_scheduler = django_rq.get_scheduler('default')
                jobs = rq_scheduler.get_jobs()

                functions = defaultdict(lambda: list())
                map(lambda x: functions[x.func].extend([x.meta.get('interval'), x.timeout,]), jobs)

                if not timeout:
                    default_timeout = global_settings.RQ_QUEUES.get('DEFAULT_TIMEOUT')
                    if default_timeout:
                        timeout = default_timeout
                    else:
                        timeout = 360

                if f not in functions or interval not in functions[f] or functions[f][1] != timeout or len(functions[f]) > 2:
                    logger.info('Rescheduling job {} with interval: {}s'.format(f.func_name, interval))
                    # clear all scheduled jobs for this function
                    map(rq_scheduler.cancel, filter(lambda x: x.func==f, jobs))

                    # schedule with new interval and timeout
                    return rq_scheduler.schedule(datetime.datetime.now(), f, interval=interval, timeout=timeout)
                else:
                    logger.info('Job already scheduled every {}s: {}'.format(interval, f.func_name))
            f.enqueue_at = enqueue_at
            f.delay = delay
            f.schedule_once = schedule_once
            return f

    def job(func_or_queue, connection=None, *args, **kwargs):
        """
        The same as RQ's job decorator, but it works automatically works out
        the ``connection`` argument from RQ_QUEUES.

        And also, it allows simplified ``@job`` syntax to put job into
        default queue.
        """
        if callable(func_or_queue):
            func = func_or_queue
            queue = 'default'
        else:
            func = None
            queue = func_or_queue

        try:
            from django.utils import six
            string_type = six.string_types
        except ImportError:
            # for django lt v1.5 and python 2
            string_type = basestring

        if isinstance(queue, string_type):
            try:
                queue = get_queue(queue)
                if connection is None:
                    connection = queue.connection
            except KeyError:
                pass

        decorator = _rq_job(queue, connection=connection, *args, **kwargs)
        if func:
            return decorator(func)
        return decorator
    return job(func_or_queue, connection, *args, **kwargs)
