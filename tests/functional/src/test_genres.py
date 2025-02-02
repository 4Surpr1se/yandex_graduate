import time
import uuid
from http import HTTPStatus

import httpx
import pytest
from settings import test_settings

pytestmark = pytest.mark.asyncio


BASE_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/genres"


async def test_get_genres_list(auth_cookies):
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, cookies=auth_cookies)
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert isinstance(data, list)
        if data:
            genre = data[0]
            assert "uuid" in genre
            assert "name" in genre
            assert "description" in genre


@pytest.fixture(scope="module")
async def existing_genre_id(auth_cookies):
    async with httpx.AsyncClient() as client:
        response_single = await client.get(BASE_URL, params={"page_size": "1", "page_number": 1}, cookies=auth_cookies)
        assert response_single.status_code == HTTPStatus.OK
        genre = response_single.json()
        return genre[0]['uuid'] if genre else None


@pytest.mark.parametrize(
    "genre_id, expected_status, expected_response",
    [
        # Параметры для успешного запроса
        (None, HTTPStatus.OK, None),

        # Параметры для запросов, когда жанр не найден
        (uuid.uuid4(), HTTPStatus.NOT_FOUND, {
         "detail": "Genre not found"}),  # UUID не существует
        ('12412', HTTPStatus.NOT_FOUND, {
         "detail": "Genre not found"})  # Некорректный ID
    ]
)
async def test_get_genre_by_id(genre_id, expected_status, expected_response, existing_genre_id, auth_cookies):
    if genre_id is None:
        genre_id = await existing_genre_id

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/{genre_id}", cookies=auth_cookies)
        assert response.status_code == expected_status
        if expected_response:
            assert response.json() == expected_response
        elif expected_status == HTTPStatus.OK:
            data = response.json()
            assert "uuid" in data
            assert data["uuid"] == str(genre_id)
            assert "name" in data


async def test_search_uses_cache(redis_client, auth_cookies):
    redis_client.flushdb()

    async with httpx.AsyncClient() as client:
        start_time = time.time()
        response = await client.get(BASE_URL, cookies=auth_cookies)
        end_time = time.time()
        assert response.status_code == HTTPStatus.OK
        initial_time = end_time - start_time

        start_time = time.time()
        response = await client.get(BASE_URL, cookies=auth_cookies)
        end_time = time.time()
        assert response.status_code == HTTPStatus.OK
        cached_time = end_time - start_time
        assert cached_time < initial_time
