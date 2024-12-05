import logging
from http import HTTPStatus
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import (
    WebhookNotificationEventType,
    WebhookNotificationFactory,
)

from src.db.postgres import get_session
from src.extras.enums import Transaction_Status, Transaction_Type
from src.models.payment import Transaction
from src.schemas.payment import RequestPayment, RequestSubscription
from src.services.notification_integration_service import send_notification
from src.services.payment_service import (
    PaymentService,
    get_ngrok_url,
    get_payment_service,
)


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/create-subscription')
async def create_subscription(
        payment: RequestSubscription,
        session: AsyncSession = Depends(get_session),
        payment_service: PaymentService = Depends(get_payment_service),
):
    try:
        transaction_id = uuid4()
        transaction = Transaction(
            id=transaction_id,
            user_id=payment.user_id,
            status=Transaction_Status.pending,
            type=Transaction_Type.subscription,
        )

        result = await payment_service.create_subscription(payment, transaction, session)

        return {
            "transaction_id": transaction_id,
            "status": "Payment initialization successful",
            **result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment: {str(e)}"
        )


@router.post('/create-payment')
async def create_payment(
        payment: RequestPayment,
        session: AsyncSession = Depends(get_session),
        payment_service: PaymentService = Depends(get_payment_service),
):
    try:
        transaction_id = uuid4()
        transaction = Transaction(
            id=transaction_id,
            user_id=payment.user_id,
            amount=payment.amount,
            currency=payment.currency,
            status=Transaction_Status.pending,
            type=Transaction_Type.movie,
        )

        result = await payment_service.create_payment(payment, transaction, session)

        return {
            "transaction_id": transaction_id,
            "status": "Payment initialization successful",
            **result,
        }

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment: {str(e)}"
        )


@router.post('/webhook')
async def webhook_handler(
        request: Request,
        session: AsyncSession = Depends(get_session),
        payment_service: PaymentService = Depends(get_payment_service),
):
    try:
        forwarded_for = request.headers.get("X-Forwarded-For")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else request.client.host

        logger.info(f"Received webhook from IP: {client_ip}")

        if not SecurityHelper().is_ip_trusted(client_ip):
            logger.warning(f"Untrusted IP: {client_ip}")
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="IP address not trusted"
            )

        event_json = await request.json()
        notification_object = WebhookNotificationFactory().create(event_json)
        response_object = notification_object.object

        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            await payment_service.update_transaction_status(
                transaction_id=UUID(response_object.metadata["transaction_id"]),
                status=Transaction_Status.succeeded,
                session=session,
            )
            if user_mail:=response_object.metadata.get("user_mail"):
                send_notification(user_mail)
            if (response_object.metadata.get("subscription_id") and
                    response_object.payment_method.saved):
                await payment_service.set_next_subscription(
                    user_id=UUID(response_object.metadata["user_id"]),
                    user_mail=response_object.metadata.get("user_mail"),
                    subscription_id=UUID(response_object.metadata["subscription_id"]),
                    captured_at=response_object.captured_at,
                    payment_method_id=response_object.payment_method.id,
                    session=session,
                )
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            await payment_service.update_transaction_status(
                transaction_id=UUID(response_object.metadata["transaction_id"]),
                status=Transaction_Status.failed,
                session=session,
            )

        elif notification_object.event == WebhookNotificationEventType.PAYMENT_WAITING_FOR_CAPTURE:
            await payment_service.update_transaction_status(
                transaction_id=UUID(response_object.metadata["transaction_id"]),
                status=Transaction_Status.pending,
                session=session,
            )
        elif notification_object.event == WebhookNotificationEventType.REFUND_SUCCEEDED:
            pass

        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Unknown webhook event"
            )

        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Webhook processing failed"
        )


@router.post('/confirm/{payment_id}')
async def confirm_payment(
        payment_id: str,
        amount: dict = None,
        session: AsyncSession = Depends(get_session),
        payment_service: PaymentService = Depends(get_payment_service),
):
    try:
        result = await payment_service.confirm_payment(payment_id, amount)
        return {
            "status": "Payment confirmed",
            "payment_id": payment_id,
            "details": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error confirming payment: {str(e)}"
        )


@router.post('/cancel/{payment_id}')
async def cancel_payment(
        payment_id: str,
        session: AsyncSession = Depends(get_session),
        payment_service: PaymentService = Depends(get_payment_service),
):
    try:
        result = await payment_service.cancel_payment(payment_id)
        return {
            "status": "Payment canceled",
            "payment_id": payment_id,
            "details": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Error canceling payment: {str(e)}"
        )


@router.get('/ngrok-url')
async def list_webhooks():
    try:
        response = get_ngrok_url()
        return {
            "ngrok-url": response,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting url: {str(e)}"
        )
