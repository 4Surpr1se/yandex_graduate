from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: str
    postgres_database: str
    postgres_user: str
    postgres_password: str

    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()