from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.notifications import router as notifications_router
from src.db.base import create_tables
from src.services.message_queue import MessageQueueService
from src.core.config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_tables()

    message_queue_service = MessageQueueService()

    for queue in settings.queue_list:
        message_queue_service.initialize_queue(queue)
    yield


app = FastAPI(
    title="Notification Service",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(notifications_router, prefix="/api/notifications")
