from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    elastic_host: str = '127.0.0.1'
    elastic_port: int = 9200
    redis_host: str
    redis_port: str
    project_name: str = 'films'
    auth_service_url: str = 'http://auth_service:8000'
    agent_host_name: str
    agent_port: int
    enable_tracer: bool = False

    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = ConfigSettings()
