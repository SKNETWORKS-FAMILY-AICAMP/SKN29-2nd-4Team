from fastapi import FastAPI
from contextlib import asynccontextmanager

from back.app.api.health_router import router as health_router

from back.app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("🚀 Starting application...")
    # 예: DB 연결, 모델 로딩
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

    return app


app = create_app()