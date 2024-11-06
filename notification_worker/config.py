from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    smtp_server: str
    smtp_port: int
    smtp_user: str
    websocket_host: str = "localhost"
    websocket_port: int = 6789
    rabbitmq_host: str = "localhost"
    rabbitmq_queue: str = "notifications"
    sendinblue_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()