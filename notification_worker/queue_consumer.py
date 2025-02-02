import pika
import time
from service import NotificationService
from config import settings
import logging

def callback(ch, method, properties, body):
    service = NotificationService()
    service.process_message(body, properties)

def start_queue_consumer(queue_name):
    connection = None
    for i in range(5):
        try:
            credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.rabbitmq_host,
                    port=5672,
                    credentials=credentials
                )
            )
            break
        except pika.exceptions.AMQPConnectionError as e:
            logging.info(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
    
    if connection is None:
        logging.info("Failed to connect to RabbitMQ after several attempts.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    logging.info(f"Waiting for messages in RabbitMQ queue '{queue_name}'...")
    channel.start_consuming()
