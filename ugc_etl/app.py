import logging
from kafka import KafkaConsumer
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

def insert_data_to_clickhouse(user_id, event_type, event_data):
    clickhouse_client.execute('''
        INSERT INTO user_events (user_id, event_type, event_data, timestamp)
        VALUES (%s, %s, %s, now())
    ''', (user_id, event_type, json.dumps(event_data)))

def consume_kafka_messages():
    consumer = KafkaConsumer(
        settings.kafka_clicks_topic,
        settings.kafka_page_views_topic,
        settings.kafka_custom_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )

    for message in consumer:
        data = message.value
        logging.info(f"Получено сообщение: {data}")

        user_id = data.get('user_id')
        if message.topic == settings.kafka_clicks_topic:
            event_type = 'click'
        elif message.topic == settings.kafka_page_views_topic:
            event_type = 'page_view'
        else:
            event_type = 'custom_event'

        insert_data_to_clickhouse(user_id, event_type, data)

def job():
    logging.info("Запуск обработки сообщений")
    consume_kafka_messages()

if __name__ == '__main__':
    create_clickhouse_table()

    scheduler = BlockingScheduler()
    # Запуск задачи через указанный интервал
    scheduler.add_job(job, 'interval', minutes=settings.job_interval_minutes)
    scheduler.start()
    