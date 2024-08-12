import time
from elasticsearch import Elasticsearch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f"http://{test_settings.elastic_host}:{test_settings.elastic_port}", verify_certs=False)
    max_wait_time = 60 
    start_time = time.time()

    while True:
        if es_client.ping():
            es_client.close()
            print("Elasticsearch is up and running.")
            break
        elif time.time() - start_time > max_wait_time:
            es_client.close()
            print("Timeout: Could not connect to Elasticsearch within the allowed time.")
            break
        time.sleep(1)