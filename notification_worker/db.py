import psycopg2
from psycopg2.extras import RealDictCursor
from config import settings

class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            host=settings.postgres_host,
            port=settings.postgres_port
        )
        self.connection.autocommit = True

    def update_last_notification_send(self, notification_id):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                UPDATE notifications 
                SET last_notification_send = NOW() 
                WHERE notification_id = %s
                """,
                (notification_id,)
            )

db = Database()
