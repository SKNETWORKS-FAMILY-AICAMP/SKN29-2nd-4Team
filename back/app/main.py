from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from back.app.api.health_router import router as health_router
from back.app.api.model_router import router as model_router
from back.app.api.app_router import router as app_router
from back.app.api.lookup_router import router as lookup_router
from back.app.config import settings
from back.app.infra.db import test_connection, get_conn


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting application...")
    test_connection()
    # await init_db()
    # model.load()

    yield

    print("🛑 Shutting down application...")
    # 예: 리소스 정리
    # await close_db()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.include_router(health_router)
    app.include_router(model_router)
    app.include_router(app_router)
    app.include_router(lookup_router)
    
    return app


app = create_app()