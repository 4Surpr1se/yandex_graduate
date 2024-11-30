from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models import Discount, TaxRate


def get_active_discounts(session: Session, item_id: int):
    """Получить минимальную активную скидку для элемента."""
    now = datetime.utcnow()
    discounts = (
        session.query(Discount)
        .filter(
            Discount.start_date <= now,
            Discount.end_date >= now,
            Discount.item_id == item_id
        )
        .all()
    )
    if discounts:
        min_discount = min(discounts, key=lambda d: d.value)
        return {"type": min_discount.type.name, "value": min_discount.value}
    return None 

def calculate_price(item_id: int, base_price: float, country: str, session: Session):
    """Рассчитать итоговую цену для товара."""
    discount_value = get_active_discounts(session, item_id)
    tax_rate = get_tax_rate_by_country(session, country)
    final_price = calculate(base_price, discount_value, tax_rate)

    return {
        "original_price": base_price,
        "final_price": final_price,
        "tax_rate": tax_rate,
        "discount_applied": discount_value or {"type": None, "value": 0},
        "country": country or "Unknown"
    }


def apply_discount(price: Decimal, discount: Discount) -> Decimal:
        """
        Применяет одну скидку к цене.
        Поддерживает два типа скидок:
        - percentage: процент от цены
        - fixed: фиксированная сумма
        """
        if not discount: 
            return price

        if discount["type"] == "percentage":
            price -= price * Decimal(discount["value"]) / 100
        elif discount["type"] == "fixed":
            price -= Decimal(discount["value"])

        return max(price, Decimal(0)) 


def calculate(base_price: float, discount: Discount, tax_rate: Decimal) -> float:
    """
    Рассчитывает итоговую цену с учетом скидки и налогов.
    """
    base_price = Decimal(base_price)
    price_after_discount = apply_discount(base_price, discount)
    tax_rate = Decimal(tax_rate)
    final_price = price_after_discount + (price_after_discount * tax_rate / 100)
    return round(final_price, 2)


def get_tax_rate_by_country(session: Session, country: Optional[str]) -> float:
    """Получить налоговую ставку для указанной страны."""
    if country:
        tax_rate = session.query(TaxRate).filter_by(country=country).first()
        if tax_rate:
            return tax_rate.rate
    return 0