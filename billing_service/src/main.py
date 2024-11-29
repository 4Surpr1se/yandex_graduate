from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.payment import router as payment_route


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    lifespan=lifespan,
)

app.include_router(payment_route, prefix="/api/v1/payment")
