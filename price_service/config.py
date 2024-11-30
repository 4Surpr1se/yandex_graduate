from pydantic import PostgresDsn
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Settings(BaseSettings):
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432  
    POSTGRES_DATABASE: str = "billing_db"
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "123qwe"

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"

    class Config:
        env_file = ".env" 
        env_file_encoding = 'utf-8'  
        case_sensitive = True 

settings = Settings()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)