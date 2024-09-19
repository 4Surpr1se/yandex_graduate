from http import HTTPStatus

import httpx
import pytest
import redis

from .settings import test_settings


@pytest.fixture(scope='function')
def redis_client():
    client = redis.Redis(host=test_settings.redis_host, port=test_settings.redis_port, decode_responses=True)
    yield client
    client.flushdb() 


@pytest.fixture(scope="module")
def auth_cookies():
    login_url = f"{test_settings.auth_service_url}/api/auth/login"
    with httpx.Client() as client:
        response = client.post(login_url, json={
            "login": test_settings.test_user_login,
            "password": test_settings.test_user_password
        })

    assert response.status_code == HTTPStatus.OK
    cookies = response.cookies
    cookies_dict = {key: value for key, value in cookies.items()}

    return cookies_dict
