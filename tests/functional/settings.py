from pydantic import Field
from pydantic_settings import BaseSettings
import os
import sys 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from testdata.es_mapping import es_index_mapping


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    redis_host: str = Field('http://127.0.0.1:6379', env='REDIS_HOST')
    es_index: str = 'movies_test'
    es_index_mapping: dict = es_index_mapping

test_settings = TestSettings() 