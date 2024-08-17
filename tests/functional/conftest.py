import pytest
import redis

from .settings import test_settings


@pytest.fixture(scope='function')
def redis_client():
    client = redis.Redis(host=test_settings.redis_host, port=test_settings.redis_port, decode_responses=True)
    yield client
    client.flushdb() 
