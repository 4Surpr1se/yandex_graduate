from contextlib import asynccontextmanager

import uvicorn
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

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
