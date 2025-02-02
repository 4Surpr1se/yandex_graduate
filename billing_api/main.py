from fastapi import FastAPI, HTTPException
from services import (get_film_price, get_subscription_price,
                      initiate_payment, cancel_subscription,
                      get_user_id_from_token, get_user_mail_from_token)
from schemas import FilmPaymentRequest, SubscriptionPaymentRequest, CancelSubscriptionRequest
from fastapi import Depends
from http import HTTPStatus

app = FastAPI()


@app.post("/payment/film",
          summary="Создание платежа за фильм",
          description="Эндпоинт используется для создания платежа за фильм. Принимает ID фильма и страну пользователя.")
async def create_film_payment(request: FilmPaymentRequest, user_id: str = Depends(get_user_id_from_token),
                              user_mail: str | None = Depends(get_user_mail_from_token)):
    try:
        film_price = get_film_price(request.country, request.film_id)

        payment_data = {
            "user_id": user_id,
            "amount": film_price["final_price"],
            "currency": "RUB",
            "description": f"Payment for film {request.film_id}",
            "payment_method": "bank_card",
            "transaction_type": "movie",
            "user_mail": user_mail,
            "movie_id": request.film_id
        }

        payment_response = initiate_payment(payment_data)

        return payment_response
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/payment/subscription",
          summary="Создание платежа за подписку",
          description="Эндпоинт используется для создания платежа за подписку. Принимает тип подписки и страну пользователя.")
async def create_subscription_payment(request: SubscriptionPaymentRequest,
                                      user_id: str = Depends(get_user_id_from_token),
                                      user_mail: str | None = Depends(get_user_mail_from_token)):
    try:
        subscription_price = get_subscription_price(request.country, request.subscription_type)

        payment_data = {
            "user_id": user_id,
            "amount": subscription_price["final_price"],
            "currency": "RUB",
            "description": f"Subscription payment for {request.subscription_type}",
            "payment_method": "bank_card",
            "transaction_type": "subscription",
            "user_mail": user_mail,
        }

        payment_response = initiate_payment(payment_data)

        return payment_response
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/payment/cancel-subscription",
          summary="Отмена подписки",
          description="Этот эндпоинт отменяет подписку пользователя по предоставленному ID подписки.")
async def cancel_subscription_endpoint(request: CancelSubscriptionRequest):
    try:
        cancel_response = cancel_subscription(request.subscription_id)

        return cancel_response
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
