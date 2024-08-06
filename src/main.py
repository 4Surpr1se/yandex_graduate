from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from contextlib import asynccontextmanager

from api.v1 import films, genres, persons
from core.config import config
from db import elastic, redis

@asynccontextmanager
async def lifespan():
    redis.redis = Redis(host=config.redis_host, port=config.redis_port)
    elastic.es = AsyncElasticsearch([{
        'host': config.elastic_host,
        'port': config.elastic_port,
        'scheme': 'http'
    }])
    yield
    await redis.redis.close()
    await elastic.es.close()
    
app = FastAPI(
    title=config.config.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)
    

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
