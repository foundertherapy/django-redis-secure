from __future__ import (division, unicode_literals)
from functools import wraps
from collections import defaultdict
import logging
import datetime

from django.conf import settings as global_settings

import django_rq
from django_rq.queues import get_queue
import rq.utils
from rq.compat import string_types
from rq.defaults import DEFAULT_RESULT_TTL
from rq.queue import Queue

from .serializer import default_secure_serializer as secure_serializer


logger = logging.getLogger(__name__)


def execute(method_name, *args, **kwargs):
    return rq.utils.import_attribute(method_name)(*args, **kwargs)


def secure_job_proxy(*args, **kwargs):
    """
    The is a proxy method, each method wanted to be stored securely, it will be directed to this method. With first
    argument is the encrypted original method name.
    :param args: Always three parameters, first is the encrypted method name, second is the encrypted actual args,
    third is the encrypted actual kwargs
    :return: actual method return value
    """
    actual_function_name = secure_serializer.loads(args[0])
    decrypted_args = secure_serializer.loads(args[1])
    kwargs = secure_serializer.loads(args[2])
    return execute(actual_function_name, *decrypted_args, **kwargs)


def job(func_or_queue, connection=None, *args, **kwargs):
    class _rq_job(object):
        def __init__(self, queue, connection=None, timeout=None,
                     result_ttl=DEFAULT_RESULT_TTL, ttl=None):
            """A decorator that adds :
            ``delay`` method to the decorated function,
            which in turn creates a RQ job when called. Accepts a required
            ``queue`` argument that can be either a ``Queue`` instance or a string
            denoting the queue name.  For example:

                @job(queue='default')
                def simple_add(x, y):
                    return x + y

                simple_add.delay(1, 2) # Puts simple_add function into queue

            ``enqueue_at`` method, which creates RQ job to be executed in the specified argument date. ``enqueue_at``
            method take the ``target_date`` as first argument, ``scheduler_name`` as second argument optional argument,
            the later argument is used to specify which ``django_rq`` to be used to enqueue job for

            ``schedule_once`` method, schedule job once or reschedule when interval changes, if job already exists,
            this will not do anything.
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
                function_name = '{}.{}'.format(f.__module__, f.__name__)
                encrypted_args = [secure_serializer.dumps(function_name)]
                encrypted_args += [secure_serializer.dumps(args)]

                encrypted_args += [secure_serializer.dumps(kwargs)]
                return queue.enqueue_call(secure_job_proxy, args=encrypted_args, kwargs={},
                                          timeout=self.timeout, result_ttl=self.result_ttl,
                                          ttl=self.ttl, depends_on=depends_on)

            @wraps(f)
            def enqueue_at(target_date, scheduler_name='default', *args, **kwargs):
                function_name = '{0}.{1}'.format(f.__module__, f.__name__)
                encrypted_args = [secure_serializer.dumps(function_name)]
                encrypted_args += [secure_serializer.dumps(args)]

                encrypted_args += [secure_serializer.dumps(kwargs)]

                scheduler = django_rq.get_scheduler(scheduler_name)
                proxy_method_name = '{}.{}'.format(secure_job_proxy.__module__, secure_job_proxy.__name__)
                return scheduler.enqueue_at(target_date, proxy_method_name, *encrypted_args, **{})

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
