import requests
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from config import settings

# Извлечение токена из куков и декодирование
def get_user_id_from_token(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="No access token provided")

    try:
        payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        return user_id
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


# Получить стоимость фильма через price_service
def get_film_price(country: str, film_id: str) -> dict:
    response = requests.post(
        f"{settings.price_service_url}/calculate_film_price",
        json={"film_id": str(film_id), "country": country}
    )
    if response.status_code == 200:
        return response.json()  # Возвращаем данные о стоимости фильма
    else:
        raise Exception("Error getting film price")

# Получить стоимость подписки через price_service
def get_subscription_price(country: str, subscription_type: str) -> dict:
    response = requests.post(
        f"{settings.price_service_url}/calculate_subscription_price",
        json={"subscription_type": subscription_type, "country": country}
    )
    if response.status_code == 200:
        return response.json()  # Возвращаем данные о стоимости подписки
    else:
        raise Exception("Error getting subscription price")

# Инициализация платежа через billing_service
def initiate_payment(payment_data: dict) -> dict:
    response = requests.post(
        f"{settings.billing_service_url}/api/v1/payment/create-payment",
        json=payment_data
    )
    if response.status_code == 200:
        return response.json()  # Возвращаем данные о платеже
    else:
        raise Exception("Error initiating payment")

# Отмена подписки через billing_service
def cancel_subscription(subscription_id: str) -> dict:
    response = requests.post(
        f"{settings.billing_service_url}/api/v1/payment/cancel/{subscription_id}"
    )
    if response.status_code == 200:
        return response.json()  # Возвращаем результат отмены подписки
    else:
        raise Exception("Error canceling subscription")
