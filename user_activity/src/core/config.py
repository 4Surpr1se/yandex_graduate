from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    current_db: str = 'mongodb'
    mongo_user: str = 'admin'
    mongo_password: str = 'admin'
    mongo_port: int = 27022
    mongo_host: str = 'localhost'
    auth_service_url: str = "http://auth_service:8000"
    database: str = 'user_activity_db'
    refresh_token_expire_days: int = 1
    access_token_expire_minutes: int = 15

    class Config:
        env_file = '.env'


settings = Settings()
