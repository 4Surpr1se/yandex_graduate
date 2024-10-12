from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str
    kafka_clicks_topic: str = 'user_clicks'
    kafka_page_views_topic: str = 'page_views'
    kafka_custom_events_topic: str = 'custom_events'
    clickhouse_host: str = 'localhost'
    clickhouse_port: int = 9000
    clickhouse_user: str = 'default'
    clickhouse_password: str = ''
    clickhouse_database: str = 'default'
    job_interval_minutes: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
