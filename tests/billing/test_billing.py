import pytest
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8009/api/v1/payment"
TEST_USER_ID = "00000000-0000-0000-0000-000000000000"

def test_create_subscription():
    """
    Тест для создания подписки с использованием API.
    """
    payload = {
        "user_id": TEST_USER_ID,
        "subscription_id": "3fa96813-00a0-45ff-b364-54b6c2242b04",
        "description": "Test subscription",
        "payment_method": "bank_card",
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

    response = requests.post(f"{BASE_URL}/create-subscription", json=payload)

    assert response.status_code == 200, f"Ошибка при создании подписки: {response.text}"
    data = response.json()
    assert "transaction_id" in data
    assert data["status"] == "Payment initialization successful"


def test_create_payment():
    """
    Тест для создания платежа с использованием API.
    """
    payload = {
        "user_id": TEST_USER_ID,
        "amount": 50.0,
        "currency": "RUB",
        "description": "Test payment",
        "payment_method": "bank_card"
    }

    response = requests.post(f"{BASE_URL}/create-payment", json=payload)

    assert response.status_code == 200, f"Ошибка при создании платежа: {response.text}"
    data = response.json()
    assert "transaction_id" in data
    assert data["status"] == "Payment initialization successful"