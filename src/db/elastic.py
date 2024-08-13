from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class ElasticInter:
    def __init__(self):
        self.elastic: Optional[AsyncElasticsearch] = None
        self.index: Optional[str] = None

    async def _get_by_id_from_elastic(self, id: str) -> Optional[dict]:
        try:
            res = await self.elastic.get(index=self.index, id=id)
        except NotFoundError:
            return None
        return res['_source']

    async def _get_hits_from_elastic(self, body: dict) -> Optional[List[dict]]:
        try:
            res = await self.elastic.search(index=self.index, body=body)
            hits = res['hits']['hits']
        except NotFoundError:
            return None
        return hits
