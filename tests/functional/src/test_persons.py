import asyncio
import time
import uuid

import httpx
import pytest

from settings import test_settings

BASE_URL = f'http://{test_settings.service_host}:{test_settings.service_port}/api/v1'
FILMS_URL = BASE_URL + '/films'
PERSONS_URL = BASE_URL + '/persons'


def chech_person_structure(person):
    assert 'uuid' in person
    assert 'full_name' in person
    assert 'films' in person

    assert isinstance(person['uuid'], str)
    assert len(person['uuid']) == 36

    assert isinstance(person['full_name'], str)
    assert len(person['full_name'].strip()) > 0

    assert isinstance(person['films'], list)


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


@pytest.fixture(scope='module')
def existing_film_ids():
    async def get_film_ids():
        async with httpx.AsyncClient() as client:
            response = await client.get(FILMS_URL, params={'page_size': '5', 'page_number': 1})
            assert response.status_code == 200
            films = response.json()
            return [film['uuid'] for film in films]
    return asyncio.run(get_film_ids())


@pytest.fixture(scope='module')
def existing_person_ids(existing_film_ids):
    async def get_person_ids():
        async with httpx.AsyncClient() as client:
            ids = []
            for existing_film_id in existing_film_ids:
                response = await client.get(f'{FILMS_URL}/{existing_film_id}')
                assert response.status_code == 200
                films = response.json()
                actors = films['actors']
                directors = films['directors']
                writers = films['writers']
                if len(actors) > 0:
                    ids.append(actors[0]['uuid'])
                if len(directors) > 0:
                    ids.append(directors[0]['uuid'])
                if len(writers) > 0:
                    ids.append(writers[0]['uuid'])
                return ids
    return asyncio.run(get_person_ids())


@pytest.mark.asyncio
async def test_get_person_by_id(existing_person_ids):
    existing_person_id = existing_person_ids[0]
    url = f'{PERSONS_URL}/{existing_person_id}'

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.status_code == 200

    person = response.json()
    chech_person_structure(person)

    nonexistent_id = str(uuid.uuid4())
    url = f'{PERSONS_URL}/{nonexistent_id}'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_films_by_person(existing_person_ids):
    existing_person_id = existing_person_ids[0]
    url = f'{PERSONS_URL}/{existing_person_id}/film'

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.status_code == 200

    films = response.json()
    for film in films:
        check_films_structure(film)

    nonexistent_id = str(uuid.uuid4())
    url = f'{PERSONS_URL}/{nonexistent_id}/film'
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_person_uses_cache(existing_person_ids, redis_client):
    redis_client.flushdb()

    async with httpx.AsyncClient() as client:
        # first request
        start_time = time.time()
        for existing_person_id in existing_person_ids:
            response = await client.get(f'{PERSONS_URL}/{existing_person_id}')
            assert response.status_code == 200
        end_time = time.time()
        initial_time = end_time - start_time

        # second request
        start_time = time.time()
        for existing_person_id in existing_person_ids:
            response = await client.get(f'{PERSONS_URL}/{existing_person_id}')
            assert response.status_code == 200
        assert response.status_code == 200

        end_time = time.time()
        cached_time = end_time - start_time

        # second request schould be faster
        assert cached_time < initial_time
