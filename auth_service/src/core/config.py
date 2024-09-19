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
    nginx_url: str = 'http://nginx:80'
    google_client_id: str
    google_secret_file_path: str = 'client_secret_75628477629-k3g90vipls2qpmlnnj1aodn935sg2e49.apps.googleusercontent.com.json'
    redis_url: str = "redis://auth_redis:6379/0"


    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = ConfigSettings()
