import uuid
import asyncio
import uuid

import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from settings import test_settings

pytestmark = pytest.mark.asyncio


async def test_search():

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [
            {'id': '1234b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Action'},
            {'id': '12311f22-121e-44a7-b78f-b19191810fbf', 'name': 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
        ]
    } for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': test_settings.es_index, '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    es_client = AsyncElasticsearch(
        hosts=f"http://{test_settings.elastic_host}:{test_settings.elastic_port}", verify_certs=False)
    if await es_client.indices.exists(index=test_settings.es_index):
        await es_client.indices.delete(index=test_settings.es_index)
    await es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)

    updated, errors = await async_bulk(client=es_client, actions=bulk_query)

    if errors:
        raise Exception('Ошибка записи данных в Elasticsearch')

    await asyncio.sleep(1)

    search_query = {
        "size": 100,
        "query": {
            "match_all": {}
        }
    }
    response = await es_client.search(index=test_settings.es_index, body=search_query)
    await es_client.close()

    assert response['hits']['total']['value'] == 60
    assert len(response['hits']['hits']) == 60
