import requests
import secrets
import string
from settings import test_settings

def generate_complex_password(length=12):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for i in range(length))

def test_user_registration_and_update():
   
    # Шаг 1: Регистрация пользователя с рандомным паролем
    initial_password = generate_complex_password()
    username = "test"
    registration_data = {
        "login": username,
        "password": initial_password,
        "first_name": "Test",
        "last_name": "Test"
    }
    
    response = requests.post(f"{test_settings.auth_service_url}/api/users/signup", json=registration_data)
    assert response.status_code == 201  # Успешная регистрация
    user_data = response.json()
    assert 'id' in user_data  # Проверка, что пользователь успешно создан

    # Шаг 2: Логин под зарегистрированным пользователем
    login_data = {
        "username": username,
        "password": initial_password
    }
    
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/login", json=login_data)
    assert response.status_code == 200  # Успешный логин

    cookies = response.cookies
    assert 'access_token' in cookies
    assert 'refresh_token' in cookies
    
    # Шаг 3: Смена логина
    new_username = "test2"
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/update-login", json={"new_user_login": new_username}, cookies=cookies)
    assert response.status_code == 200
    update_response = response.json()
    assert update_response['status'] == 'success'

    # Шаг 4: Смена пароля
    new_password = generate_complex_password()
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/update-password", json={"new_user_password": new_password}, cookies=cookies)
    assert response.status_code == 200
    update_response = response.json()
    assert update_response['status'] == 'success'

    # Шаг 5: Попытка логина с новым логином и паролем
    login_data = {
        "username": new_username,
        "password": new_password
    }
    
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/login", json=login_data)
    assert response.status_code == 200
    
        # Шаг 6: Удаление access_token и обновление через refresh
    del cookies['access_token']  # Удаляем access_token из кук
    
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/refresh", cookies=cookies)
    assert response.status_code == 200  # Проверка успешного обновления токена
    
    new_cookies = response.cookies
    assert 'access_token' in new_cookies
    assert new_cookies['access_token'] != cookies.get('access_token')

    # Шаг 7: Логаут
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/logout", cookies=new_cookies)
    assert response.status_code == 200

    assert 'access_token' not in response.cookies
    assert 'refresh_token' not in response.cookies

    login_data = {
        "username": new_username,
        "password": new_password
    }
    
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/login", json=login_data)
    assert response.status_code == 200  # Успешный логин

