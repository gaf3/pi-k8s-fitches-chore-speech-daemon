"""
Main module for daemon
"""

import os
import time
import traceback

import pi_k8s_fitches.chore_redis

class Daemon(object):
    """
    Main class for daemon
    """

    def __init__(self):

        self.chore_redis = pi_k8s_fitches.chore_redis.ChoreRedis(
            host=os.environ['REDIS_HOST'],
            port=int(os.environ['REDIS_PORT']),
            channel=os.environ['REDIS_CHANNEL']
        )
        self.sleep = int(os.environ['SLEEP'])

    def process(self):
        """
        Processes active chores for remindeds
        """

        for chore in self.chore_redis.list():
            if "end" not in chore:
                self.chore_redis.remind(chore)
    
    def run(self):
        """
        Runs the daemon
        """

        while True:
            try:
                self.process()
                time.sleep(self.sleep)
            except Exception as exception:
                print(str(exception))
                print(traceback.format_exc())
