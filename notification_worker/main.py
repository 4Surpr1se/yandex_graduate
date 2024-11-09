import asyncio
from multiprocessing import Process
from websocket_server import start_websocket_server
from queue_consumer import start_queue_consumer
import logging
import time
from config import settings

def run_websocket_server():
    logging.info("Starting WebSocket server...")
    asyncio.run(start_websocket_server())

def run_queue_consumer(queue_name):
    logging.info((f"Starting queue consumer for queue {queue_name}...")
    start_queue_consumer(queue_name)


if __name__ == "__main__":
    websocket_process = Process(target=lambda: asyncio.run(start_websocket_server()))
    websocket_process.start()
    
    logging.info("Listening to queues:", settings.parsed_queues)

    queue_processes = []
    for queue_name in settings.parsed_queues:
        queue_process = Process(target=run_queue_consumer, args=(queue_name,))
        queue_processes.append(queue_process)
        queue_process.start()

    websocket_process.join()
    for process in queue_processes:
        process.join()
