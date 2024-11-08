from handlers import RegistrationHandler, LikeHandler, DislikeHandler, NewEpisodeHandler
from config import settings
import pika
import schedule
import json
import time

class NotificationGenerator:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.rabbitmq_host))
        self.channel = self.connection.channel()
        
        self.queues = {
            'users.register': RegistrationHandler(api_url=settings.notification_api_url, email_sender=settings.email_sender),
            'user.liked': LikeHandler(),
            'series.new_episode': NewEpisodeHandler(),
        }

        for queue_name in self.queues:
            self.channel.queue_declare(queue=queue_name, durable=True)

    def consume_messages(self, queue_name):
        handler = self.queues[queue_name]

        def callback(ch, method, properties, body):
            message = json.loads(body)
            handler.handle(message)

        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def schedule_jobs(self):
        schedule.every(5).seconds.do(lambda: self.consume_messages('users.register'))
        schedule.every(10).seconds.do(lambda: self.consume_messages('user.liked'))
        schedule.every(15).seconds.do(lambda: self.consume_messages('series.new_episode'))

    def start(self):
        self.schedule_jobs()
        print("Notification generator started with scheduler")
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    generator = NotificationGenerator()
    generator.start()
