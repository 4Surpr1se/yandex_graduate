import pika
import uuid

from config import settings


def create_connection():
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST, port=settings.RABBITMQ_PORT, credentials=credentials
    )
    return pika.BlockingConnection(parameters)


def send_message(queue_name, message_body, headers=None):
    connection = create_connection()
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

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
    connection.close()
