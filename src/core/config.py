from pydantic import Field
from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    elastic_host: str = Field(
        default='elasticsearch', env='ELASTIC_HOST')
    elastic_port: int = Field(default=9200, env='ELASTIC_PORT')
    redis_host: str = Field(env='REDIS_HOST')
    redis_port: str = Field(env='REDIS_PORT')
    project_name: str = 'films'

    class Config:
        env_file = "../.env"
        extra = "ignore"

config = ConfigSettings()
 