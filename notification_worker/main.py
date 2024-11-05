import asyncio
from multiprocessing import Process
from websocket_server import start_websocket_server
from queue_consumer import start_queue_consumer

if __name__ == "__main__":
    websocket_process = Process(target=lambda: asyncio.run(start_websocket_server()))
    queue_consumer_process = Process(target=start_queue_consumer)

    websocket_process.start()
    queue_consumer_process.start()

    websocket_process.join()
    queue_consumer_process.join()
