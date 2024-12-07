import logging
import uuid
from datetime import datetime

from dateutil import relativedelta
import aiohttp

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import ApiError

from src.core.config import settings
from src.extras.enums import Transaction_Status, Subscription_Status
from src.models.payment import Transaction, Subscription, UserSubscription
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
                        "return_url": settings.payment_redirect
                    },
                    "description": payment_data.description,
                    "metadata": {
                        "user_id": str(payment_data.user_id),
                        "transaction_id": str(transaction.id),
                        "user_mail": str(payment_data.user_mail),
                    },
                }
            )

            return await self.log_transaction(response, transaction, session)
        except ApiError as e:
            logger.error(f"YooKassa Error: {e}")
            raise RuntimeError(f"YooKassa Error: {e}")
        except Exception as e:
            logger.error(f"Error while creating payment: {e}")
            raise RuntimeError(f"Error while creating payment: {e}")

    async def renew_subscription(self, transaction, user_subscription, session):
        try:
            logger.info(f"Renewing subscription: {transaction.id}")

            amount = user_subscription.subscription.base_price
            currency = user_subscription.subscription.base_currency

            transaction.subscription_id = user_subscription.subscription_id
            transaction.amount = amount
            transaction.currency = currency

            response = Payment.create({
                "amount": {
                    "value": amount,
                    "currency": currency
                },
                "capture": True,
                "payment_method_id": user_subscription.payment_method_id,
                "metadata": {
                    "user_id": str(user_subscription.user_id),
                    "transaction_id": str(transaction.id),
                    "subscription_id": str(user_subscription.subscription_id),
                    "user_mail": str(user_subscription.user_mail),
                },
            })

            return await self.log_transaction(response, transaction, session)
        except ApiError as e:
            logger.error(f"YooKassa Error: {e}")
            raise RuntimeError(f"YooKassa Error: {e}")
        except Exception as e:
            logger.error(f"Error while renew subscription: {e}")
            raise RuntimeError(f"Error while renew subscription: {e}")

    async def create_subscription(self, payment_data, transaction, session):

        try:
            subscription = await self._get_subscription_by_id(payment_data.subscription_id, session)
            transaction.subscription = subscription
            transaction.amount = subscription.base_price
            transaction.currency = subscription.base_currency
            response = Payment.create(
                {
                    "amount": {
                        "value": subscription.base_price,
                        "currency": subscription.base_currency
                    },
                    "payment_method_data": {
                        "type": payment_data.payment_method
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": settings.payment_redirect
                    },
                    "description": payment_data.description,
                    "capture": True,
                    "save_payment_method": True,
                    "metadata": {
                        "user_id": str(payment_data.user_id),
                        "transaction_id": str(transaction.id),
                        "subscription_id": str(subscription.id),
                        "user_mail": str(payment_data.user_mail),
                    }
                }
            )
            return await self.log_transaction(response, transaction, session)
        except ApiError as e:
            logger.error(f"YooKassa Error: {e}")
            raise RuntimeError(f"YooKassa Error: {e}")
        except Exception as e:
            logger.error(f"Error while creating subscription: {e}")
            raise RuntimeError(f"Error while creating subscription: {e}")

    async def log_transaction(self, response, transaction, session):
        transaction.status = Transaction_Status.pending
        transaction.created_at = datetime.strptime(response.created_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        logger.info(f"Payment created successfully, ID: {vars(transaction)}")
        await self.save_transaction(transaction, session)
        logger.info(f"Payment created successfully, ID: {response.id}")
        return {"yookassa_payment_id": response.id, "confirmation_url": response.confirmation.confirmation_url}

    async def _get_subscription_by_id(self, subscription_id, session):
        async with session.begin():
            result = await session.execute(
                select(Subscription).filter_by(id=subscription_id)
            )
            subscription = result.scalar_one_or_none()
            if not subscription:
                logger.error(f"Subscription {subscription_id} not found")
                raise RuntimeError(f"Subscription {subscription_id} not found")
        await session.close()
        return subscription

    async def save_transaction(self, transaction: Transaction, session: AsyncSession):
        logger.info(f"Started saving transaction ID: {transaction.id}")

        if not session.is_active:
            async with session.begin():
                session.add(transaction)
                logger.info(f"Transaction ID: {transaction.id} saved successfully")
        else:
            session.add(transaction)
            logger.info(f"Transaction ID: {transaction.id} saved successfully without starting a new transaction")
            await session.commit()
        await session.close()

    async def set_next_subscription(self, user_id, user_mail, subscription_id, captured_at,
                                    payment_method_id, session):
        async with session.begin():
            result = await session.execute(
                select(UserSubscription).filter_by(
                    user_id=user_id,
                    subscription_id=subscription_id,
                )
            )
            user_subscription = result.scalar_one_or_none()

            if not user_subscription:
                user_subscription = UserSubscription(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    subscription_id=subscription_id,
                    status=Subscription_Status.active,
                    payment_method_id=payment_method_id
                )
            if user_mail:
                user_subscription.user_mail = user_mail
            user_subscription.next_billing_date = self._get_next_billing_date(captured_at)

            session.add(user_subscription)
        await session.close()

    def _get_next_billing_date(self, date):
        return date + relativedelta.relativedelta(months=1)

    async def update_transaction_status(self, transaction_id: uuid.UUID, status: Transaction_Status,
                                        session: AsyncSession):
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

        await session.close()

    async def confirm_payment(self, payment_id: str, amount: dict = None):
        payload = {"amount": amount} if amount else {}
        response = Payment.capture(payment_id, payload)
        return response

    async def cancel_payment(self, payment_id: str):
        response = Payment.cancel(payment_id)
        return response


async def get_ngrok_url():
    try:
        logger.info("Retrieving ngrok URL")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://{settings.ngrok_host}:{settings.ngrok_port}/api/tunnels") as response:
                response.raise_for_status()
                data = await response.json()
                tunnels = data.get("tunnels", [])

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
