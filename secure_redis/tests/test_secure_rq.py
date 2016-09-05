from __future__ import unicode_literals

import mock
import datetime

import django.test

import secure_redis.secure_rq


@secure_redis.secure_rq.job
def dummy(*args, **kwargs):
    pass


class SecureRedisRQTestCase(django.test.TestCase):
    @mock.patch('secure_redis.secure_rq.execute')
    @mock.patch('rq.job.Job.save')
    def test_delay_basic(self, save_method, execute_method):
        args = [1, 2, 3, ]
        kwargs = {'param1': 'A', 'param2': 'B', }
        dummy.delay(*args, **kwargs)

    @mock.patch('rq.queue.Queue.enqueue_call')
    def test_delay_no_plain_parameters(self, enqueue_call_method):
        args = [1, 2, 3, ]
        kwargs = {'param1': 'A', 'param2': 'B', }
        dummy.delay(*args, **kwargs)
        enqueue_call_method.assert_called_once()
        self.assertEqual('secure_job_proxy', enqueue_call_method.call_args[0][0].func_name)
        # Get the intersection between sent paramters and actual ones and ensure there are no intersection
        self.assertFalse([i for i in args if i in enqueue_call_method.call_args[1]['args']])
        self.assertFalse([i for i in kwargs if i in enqueue_call_method.call_args[1]['args']])
        self.assertFalse([i for i in kwargs if i in enqueue_call_method.call_args[1]['kwargs']])

    @mock.patch('secure_redis.secure_rq.execute')
    @mock.patch('rq.job.Job.save')
    def test_delay_parameters_recovered(self, save_method, execute_method):
        args = [1, 2, 3, ]
        kwargs = {'param1': 'A', 'param2': 'B', }
        dummy.delay(*args, **kwargs)
        execute_method.assert_called_with('secure_redis.tests.test_secure_rq.dummy', *args, **kwargs)

    @mock.patch('rq_scheduler.scheduler.Scheduler.enqueue_at')
    def test_enqueue_at_called(self, enqueue_at_method):
        args = [1,2, ]
        kwargs = {'a': '1', }
        t = datetime.datetime.now()
        dummy.enqueue_at(t, 'default', *args, **kwargs)
        enqueue_at_method.assert_called_once()
        self.assertIn(t, enqueue_at_method.call_args[0])

    @mock.patch('secure_redis.secure_rq.execute')
    @mock.patch('rq.job.Job.save')
    def test_enqueue_at_executed(self, save_method, execute_method):
        args = [1,2, ]
        kwargs = {'a': '1', }
        t = datetime.datetime.now()
        job = dummy.enqueue_at(t, 'default', *args, **kwargs)
        job.perform()
        execute_method.assert_called_with('secure_redis.tests.test_secure_rq.dummy', *args, **kwargs)

    @mock.patch('rq_scheduler.scheduler.Scheduler.schedule')
    def test_scheduled_once_called(self, schedule_method):
        interval = 60
        dummy.schedule_once(interval)
        schedule_method.assert_called_once()
        self.assertIn(interval, schedule_method.call_args[1].values())
