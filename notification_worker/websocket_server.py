import asyncio
import websockets
from service import NotificationService
from config import settings

async def websocket_server(websocket, path):
    service = NotificationService()
    while True:
        message = await websocket.recv()
        service.process_message(message, websocket)

async def start_websocket_server():
    await websockets.serve(websocket_server, settings.websocket_host, settings.websocket_port)
