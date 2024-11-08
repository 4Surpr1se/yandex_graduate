from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    rabbitmq_host: str = "rabbitmq"
    notification_api_url: str = "http://notification_api:8002/api/notifications/send-notification"

    class Config:
        env_file = ".env"

settings = Settings()