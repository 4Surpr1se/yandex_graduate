from pydantic_settings import BaseSettings

from testdata.es_mapping import es_index_mapping


class TestSettings(BaseSettings):   
    redis_host: str = '127.0.0.1'
    redis_port: str = '6379'
    elastic_host: str = '127.0.0.1'
    elastic_port: str = '9200'
    es_index: str = 'movies_test'
    es_index_mapping: dict = es_index_mapping
    service_host: str = '127.0.0.1'
    service_port: str = '80'
    auth_service_url: str = 'http://127.0.0.1:8000/'
    test_user_password: str
    test_registration_login: str = 'test_registration'
    test_registration_password: str
    test_user_login: str = 'test'
    test_user_password: str
    

test_settings = TestSettings() 