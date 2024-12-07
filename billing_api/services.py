import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from config import settings
from http import HTTPStatus


# Извлечение токена из куков и декодирование
async def get_user_id_from_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="No access token provided")

    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials")


async def get_user_mail_from_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="No access token provided")

    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_mail: str = payload.get("mail")
        if user_mail is None:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials")
        return user_mail
    except JWTError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Could not validate credentials")


# Получить стоимость фильма через price_service
async def get_film_price(country: str, film_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.price_service_url}/calculate_film_price",
            json={"film_id": str(film_id), "country": country}
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()  # Возвращаем данные о стоимости фильма
        else:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error getting film price")


# Получить стоимость подписки через price_service
async def get_subscription_price(country: str, subscription_type: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.price_service_url}/calculate_subscription_price",
            json={"subscription_type": subscription_type, "country": country}
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()  # Возвращаем данные о стоимости подписки
        else:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error getting subscription price")


# Инициализация платежа через billing_service
async def initiate_payment(payment_data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.billing_service_url}/api/v1/payment/create-payment",
            json=payment_data
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()  # Возвращаем данные о платеже
        else:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error initiating payment")


# Отмена подписки через billing_service
async def cancel_subscription(subscription_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.billing_service_url}/api/v1/payment/cancel/{subscription_id}"
        )
        if response.status_code == HTTPStatus.OK:
            return response.json()  # Возвращаем результат отмены подписки
        else:
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Error canceling subscription")
