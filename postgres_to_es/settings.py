from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    batch_size: int = 100
    elastic_host: str
    elastic_port: int = 9200
    db_host: str
    db_name: str
    db_user: str
    db_password: str

    class Config:
        env_file = "../.env"
        extra = "ignore"


settings = Settings()
