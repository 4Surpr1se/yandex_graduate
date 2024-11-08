from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    POSTGRES_USE: str = "user"
    POSTGRES_PASSWORD: str = "qwe123"
    POSTGRES_DB: str = "notification"

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"


settings = Settings()
