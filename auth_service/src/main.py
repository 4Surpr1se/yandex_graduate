from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.db.postgres import create_tables
from src.core.config import settings
from src.api import user


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.models.user import User
    await create_tables()
    yield


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

# Подключаем маршруты
app.include_router(user.router, prefix="/api/users", tags=["users"])
