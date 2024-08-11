import time
from elasticsearch import Elasticsearch
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import test_settings

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=test_settings.es_host, verify_certs=False)
    while True:
        if es_client.ping():
            es_client.close()
            break
        time.sleep(1) 