import asyncio
import pytest
import aiohttp
from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy.future import select

from models import Transaction, Transaction_Status
from db import get_session
from config import settings


@pytest.fixture(scope="session")
def event_loop():
    '''''
    Fixes following error:
    RuntimeError: Task <Task pending name='Task-5' coro=<test_create_payment_with_real_db() 
    running at /home/user/Async_API_sprint_1/tests/billing/test_billing.py:94> cb=[_run_until_complete_cb() 
    at /usr/lib/python3.10/asyncio/base_events.py:184]> got Future <Future pending 
    cb=[BaseProtocol._on_waiter_completed()]> attached to a different loop
    '''''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
    
async def check_transaction_status_in_db(transaction_id, expected_status, session):
    async with session.begin():
        result = await session.execute(select(Transaction).filter_by(id=transaction_id))
        transaction = result.scalar_one_or_none()
        assert transaction is not None, "Транзакция не найдена в базе данных"
        assert transaction.status == expected_status, f"Ожидаемый статус транзакции: {expected_status}, найден: {transaction.status}"



async def check_transaction_subscription_in_db(user_id, subscription_id, session):
    async with session.begin():
        result = await session.execute(
            select(Transaction)
            .filter_by(user_id=user_id, subscription_id=subscription_id)
            .order_by(Transaction.created_at.desc())
            .limit(1)
        )
        transaction = result.scalar_one_or_none()
        assert transaction is not None, "Последняя транзакция не найдена в базе данных"
        assert transaction.status == Transaction_Status.pending, "Статус транзакции неверен"


@pytest.mark.asyncio
async def test_create_subscription():
    """
    Тест для создания подписки с использованием API и проверки базы данных.
    """
    payload = {
        "user_id": settings.test_user_id,
        "subscription_id": settings.subscription_id,
        "description": "Test subscription",
        "payment_method": "bank_card",
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{settings.billing_url}/create-subscription", json=payload) as response:
            assert response.status == 200, f"Ошибка при создании подписки: {response.text}"

            data = await response.json()
            transaction_id = data.get("transaction_id")
            assert transaction_id, "ID транзакции не возвращен в ответе"

            db_session = await get_session()
            try:
                await check_transaction_status_in_db(transaction_id, Transaction_Status.pending, db_session)
                await check_transaction_subscription_in_db(settings.test_user_id, settings.subscription_id, db_session)
            finally:
                await db_session.close()


@pytest.mark.asyncio
async def test_create_payment():
    """
    Тест для создания платежа с использованием API и проверки базы данных.
    """
    transaction_id = str(uuid4())
    payload = {
        "user_id": settings.test_user_id,
        "amount": 50.0,
        "currency": "RUB",
        "description": "Test payment",
        "payment_method": "bank_card"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{settings.billing_url}/create-payment", json=payload) as response:
            assert response.status == 200, f"Ошибка при создании платежа: {response.text}"

            data = await response.json()
            transaction_id = data.get("transaction_id")
            assert transaction_id, "ID транзакции не возвращен в ответе"

            db_session = await get_session()
            try:
                await check_transaction_status_in_db(transaction_id, Transaction_Status.pending, db_session)
            finally:
                await db_session.close()
                


