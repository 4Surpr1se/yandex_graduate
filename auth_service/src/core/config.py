from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str
    project_name: str = 'auth'
    jwt_secret_key: str 
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    redis_url: str = "redis_auth:6379/0"
    google_client_id: str
    google_client_secret: str
    

    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = ConfigSettings()
