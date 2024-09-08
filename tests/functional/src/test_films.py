import asyncio
import time
import uuid
from http import HTTPStatus

import httpx
import pytest
from settings import test_settings

pytestmark = pytest.mark.asyncio


BASE_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films"


def check_films_structure(film):
    assert 'uuid' in film
    assert 'title' in film
    assert 'imdb_rating' in film

    assert isinstance(film['uuid'], str)
    assert len(film['uuid']) == 36

    assert isinstance(film['title'], str)
    assert len(film['title'].strip()) > 0

    assert isinstance(film['imdb_rating'], (float, int))
    assert 0 < film['imdb_rating'] <= 10


@pytest.mark.parametrize(
    "params, expected_result_count",
    [
        ({"page_size": "30", "page_number": 1}, 30),
        ({"page_size": "4", "page_number": 10}, 4),
    ]
)
async def test_get_films(params, expected_result_count, auth_cookies):
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params, cookies=auth_cookies)

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == expected_result_count

    film_ids = set()

    for film in data:
        check_films_structure(film)
        assert film['uuid'] not in film_ids
        film_ids.add(film['uuid'])

    assert data[0]['imdb_rating'] >= data[1]['imdb_rating']


@pytest.fixture(scope="module")
def existing_film_id(auth_cookies):
    async def get_film_id():
        async with httpx.AsyncClient() as client:
            response1 = await client.get(BASE_URL, params={"page_size": "1", "page_number": 1}, cookies=auth_cookies)
            assert response1.status_code == HTTPStatus.OK
            films1 = response1.json()
            return films1[0]['uuid']

    return asyncio.run(get_film_id())


async def test_get_film_by_id(existing_film_id, auth_cookies):
    url = f"{BASE_URL}/{existing_film_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies=auth_cookies)

    assert response.status_code == HTTPStatus.OK

    film = response.json()

    check_films_structure(film)

    nonexistent_id = str(uuid.uuid4())
    url = f"{BASE_URL}/{nonexistent_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, cookies=auth_cookies)

    assert response.status_code == HTTPStatus.NOT_FOUND
