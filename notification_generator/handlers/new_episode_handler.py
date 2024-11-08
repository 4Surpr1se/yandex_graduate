from datetime import datetime
from base_handler import BaseHandler

class NewEpisodeHandler(BaseHandler):
    def handle(self, message):
        series_id = message.get("series_id")
        episode_id = message.get("episode_id")
        print(f"[{datetime.now()}] Processed new episode event for series {series_id}, episode {episode_id}")