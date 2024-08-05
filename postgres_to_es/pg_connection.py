import psycopg2
from logger import logger
from settings import settings

def create_pg_connection():
    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
        )
        logger.info('Successfully connected to PostgreSQL')
        return conn
    except Exception as e:
        logger.error('Error connecting to PostgreSQL: %s', e)
        return None
    
