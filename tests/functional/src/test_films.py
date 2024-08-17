import asyncio
import time
import uuid

import httpx
import pytest

from settings import test_settings

BASE_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films"

@pytest.mark.asyncio
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
    

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, expected_result_count",
    [
        ({"page_size": "30", "page_number": 1}, 30),
        ({"page_size": "4", "page_number": 10}, 4),
    ]
)
async def test_get_films(params, expected_result_count):
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
    
    assert response.status_code == 200
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
def existing_film_id():
    async def get_film_id():
        async with httpx.AsyncClient() as client:
            response1 = await client.get(BASE_URL, params={"page_size": "1", "page_number": 1})
            assert response1.status_code == 200
            films1 = response1.json()
            return films1[0]['uuid']

    return asyncio.run(get_film_id())


@pytest.mark.asyncio
async def test_get_film_by_id(existing_film_id):
    url = f"{BASE_URL}/{existing_film_id}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    assert response.status_code == 200

    film = response.json()

    check_films_structure(film)
    
    nonexistent_id = str(uuid.uuid4())
    url = f"{BASE_URL}/{nonexistent_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, expected_result_count",
    [
        ({"query": "Star Wars"}, True),
        ({"query": "Non Existent Movie"}, False),
    ]
)
async def test_search_films(params, expected_result_count):
    url = f"{BASE_URL}/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
    
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)

    if expected_result_count:
        assert len(data) > 0

        film_ids = set()

        for film in data:
            check_films_structure(film)
            assert film['uuid'] not in film_ids
            film_ids.add(film['uuid'])
    else:
        assert len(data) == 0
        

@pytest.mark.asyncio
async def test_search_uses_cache(redis_client):
    params = {"query": "Star Wars", "page_size": "5", "page_number": 1}
    redis_client.flushdb()
    
    async with httpx.AsyncClient() as client:
        # first request
        start_time = time.time()
        response = await client.get(BASE_URL + "/search", params=params)
        end_time = time.time()
        
        assert response.status_code == 200
        initial_time = end_time - start_time

        # second request
        start_time = time.time()
        response = await client.get(BASE_URL + "/search", params=params)
        end_time = time.time()
        
        assert response.status_code == 200
        cached_time = end_time - start_time

        # second request schould be faster
        assert cached_time < initial_time
     
