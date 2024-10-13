import http
import json
import logging
import uuid
from enum import StrEnum, auto

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()
logger = logging.getLogger(__name__)


class Roles(StrEnum):
    ADMIN = auto()
    SUBSCRIBER = auto()


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # url = settings.AUTH_API_LOGIN_URL
        url = 'http://auth_service:8000/api/auth/login'
        payload = {'login': username, 'password': password}
        response = requests.post(url, data=json.dumps(payload))
        if response.status_code != http.HTTPStatus.OK:
            return None

        auth_service_url = f"http://auth_service:8000/api/auth/verify_token"
        response = requests.post(auth_service_url, cookies=response.cookies)
        data = response.json()
        try:
            user, created = User.objects.get_or_create(id=data.get('user_id'), )
            user.email = data.get('email', username)
            user.first_name = data.get('first_name', 'Unknown')
            user.last_name = data.get('last_name', 'Unknown')
            user.is_staff = 'admin' in data.get('roles')
            user.is_active = data.get('is_active', True)
            user.save()
        except Exception as e:
            logger.error(f'Authentication failed with exception: {e}')
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None