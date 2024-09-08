import requests
from settings import test_settings

FILMS_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films"

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
        initial_password = test_settings.test_registration_password
        username = test_settings.test_registration_login
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

        # Шаг 3: Проверка доступа к страницам фильмов (зарегистрированный пользователь)
        # Доступ к 1 странице
        response = requests.get(FILMS_URL, params={"page_size": "4", "page_number": 1}, cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Доступ ко 2 странице
        response = requests.get(FILMS_URL, params={"page_size": "4", "page_number": 2}, cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Шаг 4: Смена логина
        new_username = test_settings.test_registration_login + '1'
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-login", params={"new_user_login": new_username}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(new_username, initial_password)

        # Шаг 5: Смена пароля
        new_password = test_settings.test_registration_password[::-1]
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-password", params={"new_user_password": new_password}, cookies=cookies)
        assert response.status_code == 200

        # Шаг 6: Логин с новым паролем
        cookies = user_login(new_username, new_password)

        # Шаг 7: Смена логина обратно
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-login", params={"new_user_login": username}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(username, new_password)

        # Шаг 8: Смена пароля обратно
        response = requests.post(f"{test_settings.auth_service_url}/api/users/update-password", params={"new_user_password": initial_password}, cookies=cookies)
        assert response.status_code == 200
        
        cookies = user_login(username, initial_password)

        # Шаг 9: Логаут
        response = requests.post(f"{test_settings.auth_service_url}/api/auth/logout", cookies=cookies)
        assert response.status_code == 200
        assert 'access_token' not in response.cookies and 'refresh_token' not in response.cookies

        # Шаг 10: Проверка доступа к страницам фильмов (незарегистрированный пользователь)
        # Доступ к 1 странице
        response = requests.get(FILMS_URL, params={"page_size": "4", "page_number": 1})
        assert response.status_code == 200
        data_first_page = response.json()
        assert len(data_first_page) > 0

        # Попытка получить доступ ко 2 странице (должен вернуть первую страницу)
        response = requests.get(FILMS_URL, params={"page_size": "4", "page_number": 2})
        assert response.status_code == 200
        data_second_page = response.json()
        assert data_second_page == data_first_page  # Проверяем, что вернулась та же самая страница
        assert len(data_second_page) > 0

    finally:
        # Удаление пользователя
        cookies = user_login(test_settings.test_registration_login, test_settings.test_registration_password)
        requests.delete(f"{test_settings.auth_service_url}/api/users/delete-user", cookies=cookies)
