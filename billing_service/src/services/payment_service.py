import logging
import time
import uuid
from datetime import datetime

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError

from src.core.config import settings
from src.extras.enums import Transaction_Status
from src.models.payment import Transaction
from src.schemas.payment import RequestPayment

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self):
        Configuration.configure(settings.shop_id, settings.yoookassa_secret)

    async def create_payment(self, payment_data: RequestPayment, transaction: Transaction, session: AsyncSession):
        try:
            logger.info(f"Creating payment with amount: {payment_data.amount}, currency: {payment_data.currency}")

            response = Payment.create(
                {
                    "amount": {
                        "value": payment_data.amount,
                        "currency": payment_data.currency
                    },
                    "payment_method_data": {
                        "type": payment_data.payment_method
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": "https://example.com/success"
                    },
                    "description": payment_data.description,
                    "metadata": {
                        "user_id": str(payment_data.user_id),
                        "transaction_id": str(transaction.id)
                    }
                }
            )
            transaction.status = Transaction_Status.pending
            transaction.created_at = datetime.strptime(response.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
            logger.info(f"Payment created successfully, ID: {vars(transaction)}")
            await self.save_transaction(transaction, session)
            logger.info(f"Payment created successfully, ID: {response.id}")
            return {"yookassa_payment_id": response.id, "confirmation_url": response.confirmation.confirmation_url}
        except ApiError as e:
            logger.error(f"YooKassa Error: {e}")
            raise RuntimeError(f"YooKassa Error: {e}")
        except Exception as e:
            logger.error(f"Error while creating payment: {e}")
            raise RuntimeError(f"Error while creating payment: {e}")

    async def save_transaction(self, transaction: Transaction, session: AsyncSession):
        logger.info(f"Started saving transaction ID: {transaction.id}")
        async with session.begin():
            session.add(transaction)
            logger.info(f"Transaction ID: {transaction.id} saved successfully")

    async def update_transaction_status(self, transaction_id: uuid.UUID, status: Transaction_Status, session: AsyncSession):
        logger.info(f"Updating transaction status for transaction ID: {transaction_id} to {status}")
        async with session.begin():
            result = await session.execute(
                select(Transaction).filter_by(id=transaction_id)
            )
            transaction = result.scalar_one_or_none()
            if not transaction:
                logger.error(f"Transaction {transaction_id} not found")
                raise RuntimeError(f"Transaction {transaction_id} not found")

            transaction.status = status
            transaction.updated_at = datetime.utcnow()
            session.add(transaction)
            logger.info(f"Transaction status updated successfully for transaction ID: {transaction_id}")

    async def confirm_payment(self, payment_id: str, amount: dict = None):
        payload = {"amount": amount} if amount else {}
        response = Payment.capture(payment_id, payload)
        return response

    async def cancel_payment(self, payment_id: str):
        response = Payment.cancel(payment_id)
        return response


def get_ngrok_url():
    try:
        logger.info("Retrieving ngrok URL")
        response = requests.get(f"http://{settings.ngrok_host}:{settings.ngrok_port}/api/tunnels")
        response.raise_for_status()
        tunnels = response.json().get("tunnels", [])

        for tunnel in tunnels:
            if tunnel.get("proto") == "https":
                logger.info(f"Ngrok URL retrieved: {tunnel.get('public_url')}")
                return tunnel.get("public_url")
    except Exception as e:
        logger.error(f"Failed to retrieve ngrok URL: {e}")
        raise RuntimeError(f"Failed to retrieve ngrok URL: {e}")

    logger.error("No active ngrok tunnels found")
    raise RuntimeError("No active ngrok tunnels found")


def get_payment_service():
    return PaymentService()
