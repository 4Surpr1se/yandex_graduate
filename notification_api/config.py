from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
