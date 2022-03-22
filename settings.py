import requests
import redis
import json, sys
import httpimport
# from 'https://github.com/firedrak/spider.git' import template

OUT_PUT_FILE_NAME = 'dataCollected.csv'

class redisCli:

    redis_host = '192.168.56.101'
    redis_port = 6379

    REDIS_CLI = redis.StrictRedis(
        host=redis_host, port=redis_port, decode_responses=True)

    def get_status(self):
        return self.REDIS_CLI.get('state')

    def start_crawling(self):
        self.REDIS_CLI.set('state', 'running')

    def stop_crawling(self):
        self.REDIS_CLI.set('state', 'stopped')

    def length_of_queue(self, key):
        return self.REDIS_CLI.llen(key)

    def redis_push(self, key, value):
        self.REDIS_CLI.lpush(key, json.dumps(value))

    def redis_pop(self, key):
        return json.loads(self.REDIS_CLI.rpop(key))

    def incr_process_count(self):
        self.REDIS_CLI.incr('process')

    def dicr_process_count(self):
        self.REDIS_CLI.decr('process')

    def get_process_count(self):
        return self.REDIS_CLI.get('process')


def first_job():
    args = sys.argv[1:]
    if args:
        url = args[0]
        with httpimport.remote_repo(["template"], url):
            import template
    
    int_job = {'url' : template.STARTING_URL, 'call_back' : 'pars'}
    redisCli().redis_push('job_queue', int_job)
