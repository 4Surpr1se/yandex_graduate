import os

from backoff_decorator import backoff
from elasticsearch import Elasticsearch
from logger import logger
from settings import settings


@backoff()
def create_es_connection():
    try:
        es = Elasticsearch(
            [{
                'host': settings.elastic_host,
                'port': settings.elastic_port,
                'scheme': 'http'
            }]
        )
        logger.info('Successfully connected to Elasticsearch')
        return es
    except Exception as e:
        logger.error('Error connecting to Elasticsearch: %s', e)
        return None


@backoff()
def upload_data(es, index_name, data):
    for record in data:
        try:
            es.index(index=index_name, id=record['id'], body=record)
            logger.info(
                'Successfully indexed/updated record in index %s with id %s', index_name, record['id'])
        except Exception as e:
            logger.error(
                'Error indexing/updating record in index %s with id %s: %s', index_name, record['id'], e)


def create_index(es, index_name, body):
    try:
        es.indices.create(index=index_name, body=body, ignore=400)
        logger.info('Created index %s in Elasticsearch', index_name)
    except Exception as e:
        logger.error('Error creating index: %s', e)
