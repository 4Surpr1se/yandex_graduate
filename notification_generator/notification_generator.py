import asyncio
import logging

class NotificationScheduler:
    async def schedule_task(self, interval, queue_name):
        while True:
            self.consume_messages(queue_name)
            await asyncio.sleep(interval)

    def start(self):
        logging.info("Notification generator started with asyncio scheduler")

        asyncio.run(self.run_scheduler())

    async def run_scheduler(self):
        tasks = [
            asyncio.create_task(self.schedule_task(30, 'users.register')),
            asyncio.create_task(self.schedule_task(60, 'user.liked')),
            asyncio.create_task(self.schedule_task(120, 'series.new_episode')),
        ]
        await asyncio.gather(*tasks)

    def consume_messages(self, queue_name):
        logging.info(f"Consuming messages from {queue_name}")

if __name__ == "__main__":
    scheduler = NotificationScheduler()
    scheduler.start()