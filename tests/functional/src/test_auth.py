import requests
from settings import test_settings


def user_login(username, password, cookies=None):
    login_data = {
        "login": username,
        "password": password
    }
    response = requests.post(f"{test_settings.auth_service_url}/api/auth/login", json=login_data, cookies=cookies)
    assert response.status_code == 200
    return response.cookies


def test_user_registration_and_update():
    cookies = None
    new_username = None
    
    try:
        # Шаг 1: Регистрация пользователя
        initial_password = test_settings.test_user_password
        username = test_settings.test_user_login
        registration_data = {
            "login": username,
            "password": initial_password,
            "first_name": "Test",
            "last_name": "Test"
        }
        response = requests.post(f"{test_settings.auth_service_url}/api/users/signup", json=registration_data)
        assert response.status_code == 201
        assert 'id' in response.json()

        # Шаг 2: Логин
        cookies = user_login(username, initial_password)

        # Шаг 3: Смена логина
        new_username = test_settings.test_user_login+'1'
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-login", params={"new_user_login": new_username}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(new_username, initial_password)

        # Шаг 4: Смена пароля
        new_password = test_settings.test_user_password[::-1]
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-password", params={"new_user_password": new_password}, cookies=cookies)
        assert response.status_code == 200

        # Шаг 5: Логин с новым паролем
        cookies = user_login(new_username, new_password)

        # Шаг 6: Смена логина обратно
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-login", params={"new_user_login": username}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(username, new_password)

        # Шаг 7: Смена пароля обратно
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-password", params={"new_user_password": initial_password}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(username, initial_password)

        # Шаг 8: Удаление access_token и обновление через refresh
        #del cookies['access_token']
        #response = requests.post(f"{test_settings.auth_service_url}/api/auth/refresh", cookies=cookies)
        #assert response.status_code == 200
        #new_cookies = response.cookies
        #assert 'access_token' in new_cookies and new_cookies['access_token'] != cookies.get('access_token')

        # Шаг 9: Логаут
        response = requests.post(f"{test_settings.auth_service_url}/api/auth/logout", cookies=cookies)
        assert response.status_code == 200
        assert 'access_token' not in response.cookies and 'refresh_token' not in response.cookies

    finally:
        # Удаление пользователя
        cookies = user_login(test_settings.test_user_login, test_settings.test_user_password)
        requests.delete(f"{test_settings.auth_service_url}/api/users/delete-user", cookies=cookies)
