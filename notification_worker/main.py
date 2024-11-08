import asyncio
from multiprocessing import Process
from websocket_server import start_websocket_server
from queue_consumer import start_queue_consumer
import time
import settings

def run_websocket_server():
    print("Starting WebSocket server...")
    asyncio.run(start_websocket_server())

def run_queue_consumer(queue_name):
    print(f"Starting queue consumer for queue {queue_name}...")
    start_queue_consumer(queue_name)

if __name__ == "__main__":
    websocket_process = Process(target=run_websocket_server)
    queue_consumer_process = Process(target=run_queue_consumer, args=(settings.parsed_queues,))

    websocket_process.start()
    queue_consumer_process.start()

    print("Processes started. Waiting for them to complete...")

    # Ожидаем завершения дочерних процессов
    websocket_process.join()
    queue_consumer_process.join()
    
    # Добавим задержку, чтобы контейнер не завершался мгновенно
    while True:
        time.sleep(10)
