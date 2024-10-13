import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from clickhouse_driver import Client
from apscheduler.schedulers.blocking import BlockingScheduler
from config import settings
import json

logging.basicConfig(level=logging.INFO)

clickhouse_client = Client(
    host=settings.clickhouse_host,
    port=settings.clickhouse_port,
    user=settings.clickhouse_user,
    password=settings.clickhouse_password,
    database=settings.clickhouse_database
)

BATCH_SIZE = 1000
batch_data = []

def create_clickhouse_table():
    clickhouse_client.execute('''
        CREATE TABLE IF NOT EXISTS user_events (
            user_id String,
            event_type String,
            event_data String,
            timestamp DateTime
        ) ENGINE = MergeTree()
        ORDER BY timestamp
    ''')

def insert_batch_to_clickhouse(batch_data):
    try:
        clickhouse_client.execute('''
            INSERT INTO user_events (user_id, event_type, event_data, timestamp)
            VALUES
        ''', batch_data)
        return True
    except Exception as e:
        logging.error(f"Ошибка при вставке данных в ClickHouse: {e}")
        return False

def consume_kafka_messages():
    try:
        consumer = KafkaConsumer(
            settings.kafka_clicks_topic,
            settings.kafka_page_views_topic,
            settings.kafka_custom_events_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=False
        )

        global batch_data

        for message in consumer:
            data = message.value

            user_id = data.get('user_id')
            if message.topic == settings.kafka_clicks_topic:
                event_type = 'click'
            elif message.topic == settings.kafka_page_views_topic:
                event_type = 'page_view'
            else:
                event_type = 'custom_event'

            batch_data.append({
                'user_id': user_id,
                'event_type': event_type,
                'event_data': json.dumps(data),
                'timestamp': 'now()'
            })

            # Выполняем вставку после накопления 1000 записей
            if len(batch_data) >= BATCH_SIZE:
                if insert_batch_to_clickhouse(batch_data):
                    consumer.commit()
                    batch_data = []
                else:
                    logging.error("Не удалось вставить батч в ClickHouse, сообщения не будут коммитированы")

    except KafkaError as e:
        logging.error(f"Ошибка при чтении данных из Kafka: {e}")

def job():
    logging.info("Запуск обработки сообщений")
    consume_kafka_messages()

if __name__ == '__main__':
    create_clickhouse_table()

    scheduler = BlockingScheduler()

    scheduler.add_job(job, 'interval', minutes=settings.job_interval_minutes)
    scheduler.start()
