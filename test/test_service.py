import unittest
import unittest.mock

import os
import json

import service

class MockChoreRedis(object):

    def __init__(self, host, port, channel):

        self.host = host
        self.port = port
        self.channel = channel

        self.chores = []
        self.reminded = []

    def list(self):

        return self.chores

    def remind(self, chore):

        self.reminded.append(chore)

class TestService(unittest.TestCase):

    @unittest.mock.patch.dict(os.environ, {
        "REDIS_HOST": "data.com",
        "REDIS_PORT": "667",
        "REDIS_CHANNEL": "stuff",
        "SLEEP": "7"
    })
    @unittest.mock.patch("pi_k8s_fitches.chore_redis.ChoreRedis", MockChoreRedis)
    def setUp(self):

        self.daemon = service.Daemon()

    def test___init___(self):

        self.assertEqual(self.daemon.chore_redis.host, "data.com")
        self.assertEqual(self.daemon.chore_redis.port, 667)
        self.assertEqual(self.daemon.chore_redis.channel, "stuff")
        self.assertEqual(self.daemon.sleep, 7)

    def test_process(self):

        self.daemon.chore_redis.chores = [
            {
                "text": "nope",
                "end": 0
            },
            {
                "text": "yep"
            }
        ]

        self.daemon.process()

        self.assertEqual(self.daemon.chore_redis.reminded, [
            {
                "text": "yep"
            }
        ])

    @unittest.mock.patch("service.time.sleep")
    @unittest.mock.patch("traceback.format_exc")
    @unittest.mock.patch('builtins.print')
    def test_run(self, mock_print, mock_traceback, mock_sleep):

        self.daemon.chore_redis.chores = [
            {
                "text": "nope",
                "end": 0
            },
            {
                "text": "yep"
            }
        ]

        mock_sleep.side_effect = [None, Exception("whoops"), Exception("whoops")]
        mock_traceback.side_effect = ["spirograph", Exception("doh")]

        self.assertRaisesRegex(Exception, "doh", self.daemon.run)

        self.assertEqual(self.daemon.chore_redis.reminded, [
            {
                "text": "yep"
            },
            {
                "text": "yep"
            },
            {
                "text": "yep"
            }
        ])
        mock_print.assert_has_calls([
            unittest.mock.call("whoops"),
            unittest.mock.call("spirograph"),
            unittest.mock.call("whoops")
        ])
