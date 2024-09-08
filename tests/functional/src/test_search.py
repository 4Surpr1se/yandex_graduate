from http import HTTPStatus
from time import time

import httpx
import pytest
from settings import test_settings

pytestmark = pytest.mark.asyncio


BASE_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/"


@pytest.mark.parametrize(
    "params, expected_result_count",
    [
        ({"query": "Star Wars", "page_size": 50}, 50),
        ({"query": "tttt"}, 0),
        ({"query": "story", "page_size": 10}, 10),
    ]
)
async def test_search_films(params, expected_result_count: int, auth_cookies):
    url = f"{BASE_URL}films/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, cookies=auth_cookies)

    if expected_result_count == 0:
        assert response.status_code == HTTPStatus.NOT_FOUND
        return

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)
    if expected_result_count > 0:
        assert len(data) > 0
        assert len(data) <= expected_result_count
        film_ids = set()
        for film in data:
            assert 'uuid' in film
            assert 'title' in film
            assert 'imdb_rating' in film

            assert isinstance(film['uuid'], str)
            assert len(film['uuid']) == 36

            assert isinstance(film['title'], str)
            assert len(film['title'].strip()) > 0

            assert isinstance(film['imdb_rating'], (float, int))
            assert 0 < film['imdb_rating'] <= 10
            assert film['uuid'] not in film_ids
            film_ids.add(film['uuid'])
    else:
        assert len(data) == 0


@pytest.mark.parametrize(
    "service_name",
    [
        "films",
        "persons"
    ]
)
async def test_search_uses_cache(redis_client, service_name, auth_cookies):
    params = {"query": "s", "page_size": "5", "page_number": 1}
    redis_client.flushdb()

    async with httpx.AsyncClient() as client:
        start_time = time()
        response = await client.get(BASE_URL + service_name + "/search", params=params, cookies=auth_cookies)
        end_time = time()
        assert response.status_code == HTTPStatus.OK
        initial_time = end_time - start_time

        start_time = time()
        response = await client.get(BASE_URL + service_name + "/search", params=params, cookies=auth_cookies)
        end_time = time()
        assert response.status_code == HTTPStatus.OK
        cached_time = end_time - start_time
        assert cached_time < initial_time


async def test_persons_search(auth_cookies):
    url = f"{BASE_URL}persons/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"query": "Ann", "page_size": 10}, cookies=auth_cookies)

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert len(data) <= 10
    for person in data:
        assert 'uuid' in person
        assert 'full_name' in person
        assert 'films' in person

        films = person['films']
        assert isinstance(films, list)
        for film in films:
            assert 'uuid' in film
            assert 'roles' in film
            assert isinstance(film['roles'], list)
            for role in film['roles']:
                assert isinstance(role, str)
