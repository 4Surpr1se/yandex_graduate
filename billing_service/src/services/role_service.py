import aiohttp

from src.core.config import settings


async def role_service(user_id, operation):
    auth_service_url = f'{settings.auth_service_url}/{user_id}/{operation}-role/'

    payload = {
        'role': 'premium',
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(auth_service_url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
            else:
                raise Exception("Error setting role")