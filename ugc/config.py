from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str
    kafka_clicks_topic: str = 'user_clicks'
    kafka_page_views_topic: str = 'page_views'
    kafka_custom_events_topic: str = 'custom_events'
    flask_host: str
    flask_port: int

    class Config:
        env_file = ".env"


settings = Settings()
