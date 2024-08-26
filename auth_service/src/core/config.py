from pydantic_settings import BaseSettings


class ConfigSettings(BaseSettings):
    postgres_host: str
    postgres_port: int
    postgres_database: str
    postgres_user: str
    postgres_password: str
    project_name: str = 'auth'

    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = ConfigSettings()
