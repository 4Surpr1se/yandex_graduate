from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str
    postgres_port: str
    postgres_database: str
    postgres_user: str
    postgres_password: str
    price_service_url: str = "http://localhost:5005"
    billing_url: str = "http://localhost:8009/api/v1/payment"
    test_user_id: str = "00000000-0000-0000-0000-000000000000"
    subscription_id: str = "3fa96813-00a0-45ff-b364-54b6c2242b04"  # monthly


    class Config:
        env_file = '.env'
        extra = 'ignore'


settings = Settings()