import json
from handlers.base_handler import BaseNotificationHandler
from db import db
import json

class PushNotificationHandler(BaseNotificationHandler):
    async def send(self, data, websocket):
        await websocket.send(json.dumps(data))
        notification_id = data.get("notification_id")
        if notification_id:
            db.update_last_notification_send(notification_id)