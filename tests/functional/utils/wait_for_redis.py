import time
import redis
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import test_settings

if __name__ == '__main__':
    redis_client = redis.StrictRedis(host=test_settings.redis_host, port=test_settings.redis_port, db=0)
    max_wait_time = 60 
    start_time = time.time()

    while True:
        try:
            if redis_client.ping():
                print("Connected to Redis.")
                break
        except redis.ConnectionError:
            pass

        if time.time() - start_time > max_wait_time:
            print("Timeout: Could not connect to Redis within the allowed time.")
            break
        time.sleep(1)
