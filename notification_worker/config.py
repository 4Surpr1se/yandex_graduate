from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    websocket_host: str = "localhost"
    websocket_port: int = 6789
    rabbitmq_host: str = "rabbitmq"
    sendinblue_api_key: str
    queues: str 
    email_sender: str 
    postgres_db: str = "notification"
    postgres_user: str = "user"
    postgres_password: str
    postgres_host: str = "notification_db"
    postgres_port: int = 5432
    
    class Config:
        env_file = ".env"
        
    @property
    def parsed_queues(self):
        return self.queues.split(',')

settings = Settings()