from fastapi import FastAPI
from alembic.config import Config
from alembic import command
from contextlib import asynccontextmanager
from src.api.notifications import router as notifications_router
from src.services.message_queue import MessageQueueService
from src.core.config import settings


alembic_cfg = Config("alembic.ini")


@asynccontextmanager
async def lifespan(_: FastAPI):

    command.upgrade(alembic_cfg, "head")

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
