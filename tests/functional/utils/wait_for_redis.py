import time
import redis
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import test_settings

if __name__ == '__main__':
    redis_client = redis.StrictRedis(host=test_settings.redis_host, port=test_settings.redis_port, db=0)
    while True:
        try:
            if redis_client.ping():
                break
        except redis.ConnectionError:
            pass
        time.sleep(1)