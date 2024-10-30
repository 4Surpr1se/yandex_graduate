import sentry_sdk
from fastapi import FastAPI
from src.api import like, favorites, review
from src.db.init_db import init_db
from contextlib import asynccontextmanager
from sentry_sdk.integrations.flask import FlaskIntegration


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    
sentry_sdk.init(integrations=[FlaskIntegration()]) 

app = FastAPI(lifespan=lifespan,
              docs_url='/api/openapi',
              openapi_url='/api/openapi.json',
              )

app.include_router(like.router, prefix="/api/like", tags=["Like"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(review.router, prefix="/api/review", tags=["Review"])
