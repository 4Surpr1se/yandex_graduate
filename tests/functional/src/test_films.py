import pytest
import httpx
import sys
import uuid
import time
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from settings import test_settings

BASE_URL = f"http://{test_settings.service_host}:{test_settings.service_port}/api/v1/films"

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
        assert 'id' in film
        assert 'title' in film
        assert 'imdb_rating' in film

        # Check id is guid
        assert isinstance(film['id'], str)
        assert len(film['id']) == 36
        assert film['id'] not in film_ids
        film_ids.add(film['id'])

        assert isinstance(film['title'], str)
        assert len(film['title'].strip()) > 0

        assert isinstance(film['imdb_rating'], (float, int))
        assert 0 < film['imdb_rating'] <= 10

    assert data[0]['imdb_rating'] >= data[1]['imdb_rating']


@pytest.mark.asyncio
async def get_existing_film_ids():
    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params={"page_size": "2", "page_number": 1})
        assert response.status_code == 200
        films = response.json()
        return [film['id'] for film in films]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "film_id, expected_status",
    [
        ("2a090dde-f688-46fe-a9f4-b781a985275e", 200), 
        ("a58961cb-0b46-49f5-8a59-20b0118f57b4", 200),
        (str(uuid.UUID(int=0)), 404),
    ]
)


async def test_get_film_by_id(film_id, expected_status):
    url = f"{BASE_URL}/{film_id}"
    
    print(film_id)
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    
    assert response.status_code == expected_status

    if response.status_code == 200:
        film = response.json()

        assert 'id' in film
        assert 'title' in film
        assert 'imdb_rating' in film

        # Check id is guid
        assert isinstance(film['id'], str)
        assert len(film['id']) == 36

        assert isinstance(film['title'], str)
        assert len(film['title'].strip()) > 0

        assert isinstance(film['imdb_rating'], (float, int))
        assert 0 < film['imdb_rating'] <= 10


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
            assert 'id' in film
            assert 'title' in film
            assert 'imdb_rating' in film

            assert isinstance(film['id'], str)
            assert len(film['id']) == 36
            assert film['id'] not in film_ids
            film_ids.add(film['id'])

            assert isinstance(film['title'], str)
            assert len(film['title'].strip()) > 0

            assert isinstance(film['imdb_rating'], (float, int))
            assert 0 < film['imdb_rating'] <= 10
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
        print(f"Initial request time: {initial_time}, Cached request time: {cached_time}")

