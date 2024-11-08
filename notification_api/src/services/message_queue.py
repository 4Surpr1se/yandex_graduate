import pika
import uuid
from src.core.config import settings


class MessageQueueService:
    def __init__(self):
        self.connection_params = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
        )

    def initialize_queue(self, queue_name: str):
        """Ensure that the queue exists, if not - declare it."""
        try:
            with pika.BlockingConnection(self.connection_params) as connection:
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)

                print(f"Queue '{queue_name}' is initialized or already exists.")
        except Exception as e:
            print(f"Error initializing queue '{queue_name}': {e}")

    def send_message(self, queue_name: str, message_body, headers: dict = None):
        try:
            with pika.BlockingConnection(self.connection_params) as connection:
                channel = connection.channel()

                if headers is None:
                    headers = {}
                headers["X-Request-Id"] = headers.get("X-Request-Id", str(uuid.uuid4()))

                properties = pika.BasicProperties(
                    delivery_mode=2,
                    headers=headers
                )

                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message_body,
                    properties=properties
                )
                print(f"Message sent to '{queue_name}'")
        except Exception as e:
            print(f"Error sending message to '{queue_name}': {e}")
