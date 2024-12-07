import asyncio
import datetime
import uuid

from sqlalchemy.future import select  # Import select for async queries
from sqlalchemy.orm import selectinload

from src.celery.celery_config import app
from src.db.postgres import get_session
from src.extras.enums import Subscription_Status
from src.models.payment import Transaction, UserSubscription
from src.services.payment_service import get_payment_service


@app.task
def subscription_renewal():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_subscription_renewal())


async def async_subscription_renewal():
    payment_service = get_payment_service()

    async for session in get_session():
        result = await session.execute(
            select(UserSubscription)
            .where(UserSubscription.next_billing_date < datetime.datetime.now())
            .options(selectinload(UserSubscription.subscription)
        ))

        expired_subscriptions = result.scalars().all()

        for expired_subscription in expired_subscriptions:
            expired_subscription.status = Subscription_Status.expired
            transaction = Transaction(
                id=uuid.uuid4(),
                user_id=expired_subscription.user_id
            )
            await payment_service.renew_subscription(transaction,
                                                     expired_subscription,
                                                     session)
        await session.close()
