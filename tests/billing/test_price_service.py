import pytest
import requests
from uuid import uuid4
from datetime import datetime, timedelta
from config import settings


@pytest.fixture
def film_calculate_price_data():
    return {
        "film_id": str(uuid4()),
        "country": "US"
    }
    
@pytest.fixture
def film_price_data():
    return {
        "item_id": str(uuid4()),
        "country": "US",
        "base_price": 100.00
    }

@pytest.fixture
def subscription_data():
    return {
        "subscription_type": "monthly",
        "country": "US",
    }

@pytest.fixture
def tax_rate_data():
    return {
        "country": "US",
        "name": "Sales Tax",
        "rate": 0.07
    }

@pytest.fixture
def discount_data():
    return {
        "film_id": str(uuid4()),
        "name": "Black Friday",
        "type": "percentage",
        "value": 20.0,
        "start_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
    }


def test_create_film_price():
    """Тест на создание цены фильма."""
    request_data = {
        "item_id": str(uuid4()),
        "country": "US",
        "base_price": 10.0
    }
    response = requests.post(f"{settings.price_service_url}/film_prices", json=request_data)
    assert response.status_code == 201
    assert "id" in response.json()

def test_calculate_film_price(film_price_data, tax_rate_data, discount_data):
    """Тест на расчет цены фильма с налогами и скидками."""
    film_id = film_price_data["item_id"]
    response = requests.post(f"{settings.price_service_url}/film_prices", json=film_price_data)
    assert response.status_code == 201

    # добавление налога и скидки
    response = requests.post(f"{settings.price_service_url}/tax_rates", json=tax_rate_data)
    assert response.status_code == 201
    discount_data["item_id"] = film_id
    response = requests.post(f"{settings.price_service_url}/discounts", json=discount_data)
    assert response.status_code == 201

    # итоговая цена
    request_data = {
        "film_id": film_id,
        "country": tax_rate_data["country"]
    }
    response = requests.post(f"{settings.price_service_url}/calculate_film_price", json=request_data)
    assert response.status_code == 200
    result = response.json()
    assert "film_id" in result
    assert "final_price" in result

def test_calculate_subscription_price(subscription_data, tax_rate_data):
    """Тест на расчет цены подписки"""
    response = requests.post(f"{settings.price_service_url}/calculate_subscription_price", json=subscription_data)
    assert response.status_code == 200
    result = response.json()
    assert "subscription_type" in result
    assert "final_price" in result
