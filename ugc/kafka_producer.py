import json
import logging
from time import sleep

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, KafkaTimeoutError, TopicAlreadyExistsError
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings

logging.basicConfig(level=logging.INFO)


def create_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id='flask-app'
    )

    topics = [
        NewTopic(
            name=settings.kafka_clicks_topic,
            num_partitions=3,
            replication_factor=3
        ),
        NewTopic(
            name=settings.kafka_page_views_topic,
            num_partitions=3,
            replication_factor=3
        ),
        NewTopic(
            name=settings.kafka_custom_events_topic,
            num_partitions=3,
            replication_factor=3
        )
    ]

    try:
        admin_client.create_topics(new_topics=topics, validate_only=False)
        logging.info("Topics created successfully.")
    except TopicAlreadyExistsError:
        logging.info("Topics already exist.")
    except Exception as e:
        logging.error(f"Error creating topics: {e}")


class MyKafkaProducer:
    def __init__(self):
        sleep(30)
        self.producer = KafkaProducer(
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: v.encode('utf-8')
        )

    @retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(20))
    def send_message(self, topic, key, value):
        try:
            future = self.producer.send(topic, key=key, value=value)
            result = future.get(timeout=10)
            logging.info(f"Message sent to topic {topic}: {value}")
            return True
        except KafkaTimeoutError as e:
            logging.error(f"Timeout error while sending message to Kafka: {e}")
            raise
        except KafkaError as e:
            logging.error(f"Kafka error while sending message to Kafka: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return False


kafka_producer = MyKafkaProducer()
