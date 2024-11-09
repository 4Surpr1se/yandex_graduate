import logging
from datetime import datetime
from base_handler import BaseHandler

class LikeHandler(BaseHandler):
    def handle(self, message):
        user_id = message.get("user_id")
        content_id = message.get("content_id")
        logging.info(f"[{datetime.now()}] Processed like event for user {user_id} on content {content_id}")
 