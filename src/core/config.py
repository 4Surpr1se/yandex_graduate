from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    redis_host: str
    redis_port: str
    project_name: str = 'films'

    class Config:
        env_file = "../.env"
        extra = "ignore"

settings = ConfigSettings()
 