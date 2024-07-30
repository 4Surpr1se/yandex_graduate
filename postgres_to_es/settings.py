from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    batch_size: int = Field(default=100, env='BATCH_SIZE')
    elasticsearch_host: str = Field(default='elasticsearch', env='ELASTIC_HOST')
    elasticsearch_port: int = Field(default=9200, env='ELASTIC_PORT')
    db_host: str = Field(env='DB_HOST')
    db_name: str = Field(env='DB_NAME')
    db_user: str = Field(env='DB_USER')
    db_password: str = Field(env='DB_PASSWORD')

    class Config:
        env_file = "../.env"
        extra = "ignore" 

settings = Settings()