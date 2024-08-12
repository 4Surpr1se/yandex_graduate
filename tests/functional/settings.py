from pydantic_settings import BaseSettings
import os
import sys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testdata.es_mapping import es_index_mapping


class TestSettings(BaseSettings):   
    redis_host: str = '127.0.0.1'
    redis_port: str = '6379'
    elastic_host: str = '127.0.0.1'
    elastic_port: str = '9200'
    es_index: str = 'movies_test'
    es_index_mapping: dict = es_index_mapping

test_settings = TestSettings() 