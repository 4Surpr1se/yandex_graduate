import aiohttp

from src.core.config import settings


async def send_notification(user_mail: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                settings.notification_service_url,
                json={
                    'title': settings.notification_title,
                    'body': settings.notification_body,
                    'channel_type': settings.notification_channel_type,
                    'message_type': settings.notification_type_billing,
                    'recipients': [user_mail],
                },
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Error sending mail: {response.status}")
        except Exception as e:
            raise Exception(f"Error sending mail: {e}")

