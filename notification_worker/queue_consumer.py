import pika
from service import NotificationService
from config import settings

def callback(ch, method, properties, body):
    service = NotificationService()
    service.process_message(body)

def start_queue_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)

    channel.basic_consume(queue=settings.rabbitmq_queue, on_message_callback=callback, auto_ack=True)
    print("Waiting for messages in RabbitMQ queue...")
    channel.start_consuming()
