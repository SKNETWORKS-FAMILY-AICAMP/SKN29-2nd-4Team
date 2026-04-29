from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # FastAPI Server
    PROJECT_NAME: str = "FastAPI App"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # DB
    DB_HOST: str
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 정의 안된 env 무시
    )

    @property
    def DATABASE_URL(self) -> SecretStr:
        return SecretStr(
            f"mysql+pymysql://{self.DB_USER}:"  # mysql driver
            f"{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()