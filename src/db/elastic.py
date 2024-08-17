from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

from db.abstract_storage import AbstractDataStorage

es: Optional[AsyncElasticsearch] = None


class ElasticDataStorage(AbstractDataStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index: str, id: str) -> Optional[dict]:
        try:
            res = await self.elastic.get(index=index, id=id)
        except NotFoundError:
            return None
        return res['_source']

    async def get_list(self, index: str, body: dict) -> Optional[List[dict]]:
        try:
            res = await self.elastic.search(index=index, body=body)
            hits = res['hits']['hits']
        except NotFoundError:
            return None
        return [hit['_source'] for hit in hits]

async def get_elastic() -> ElasticDataStorage:
    return ElasticDataStorage(es)
