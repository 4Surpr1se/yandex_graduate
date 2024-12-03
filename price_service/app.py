from flask import Flask, jsonify, request
from pydantic import ValidationError
from config import SessionLocal
from sqlalchemy.orm import Session
from models import FilmPrice, Subscription, TaxRate, Discount
from services import calculate_price
from request_models import FilmPriceRequest, SubscriptionPriceRequest, TaxRateRequest, DiscountRequest

app = Flask(__name__)

@app.route('/calculate_film_price', methods=['POST'])
def calculate_film_price():
    try:
        data = FilmPriceRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    film_id = data.film_id
    country = data.country

    with SessionLocal() as session:
        film_price = session.query(FilmPrice).filter(FilmPrice.item_id == film_id).first()
        if not film_price:
            return jsonify({"error": "Film not found"}), 404

        result = calculate_price(film_price.item_id, film_price.base_price, country, session)
    return jsonify({"film_id": film_id, **result}), 200

@app.route('/calculate_subscription_price', methods=['POST'])
def calculate_subscription_price():
    try:
        data = SubscriptionPriceRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    subscription_type = data.subscription_type
    country = data.country

    if subscription_type not in ['monthly', 'yearly']:
        return jsonify({"error": "Invalid subscription type"}), 400

    with SessionLocal() as session:
        subscription = session.query(Subscription).filter(Subscription.name == subscription_type).first()
        if not subscription:
            return jsonify({"error": "Subscription not found"}), 404

        result = calculate_price(subscription.id, subscription.base_price, country, session)
    return jsonify({"subscription_type": subscription_type, **result}), 200

# CRUD для цен фильмов
@app.route('/film_prices', methods=['POST'])
def create_film_price():
    try:
        data = FilmPriceRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        new_film_price = FilmPrice(item_id=data.item_id, base_price=data.base_price)
        session.add(new_film_price)
        session.commit()
        return jsonify({"message": "Film price created successfully", "id": new_film_price.id}), 201

@app.route('/film_prices/<uuid:id>', methods=['GET'])
def get_film_price(id):
    with SessionLocal() as session:
        film_price = session.query(FilmPrice).filter(FilmPrice.id == id).first()
        if not film_price:
            return jsonify({"error": "Film price not found"}), 404
        return jsonify({"id": film_price.id, "item_id": film_price.item_id, "base_price": film_price.base_price})

@app.route('/film_prices/<uuid:id>', methods=['PUT'])
def update_film_price(id):
    try:
        data = FilmPriceRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        film_price = session.query(FilmPrice).filter(FilmPrice.id == id).first()
        if not film_price:
            return jsonify({"error": "Film price not found"}), 404
        film_price.base_price = data.base_price
        session.commit()
        return jsonify({"message": "Film price updated successfully"})

@app.route('/film_prices/<uuid:id>', methods=['DELETE'])
def delete_film_price(id):
    with SessionLocal() as session:
        film_price = session.query(FilmPrice).filter(FilmPrice.id == id).first()
        if not film_price:
            return jsonify({"error": "Film price not found"}), 404
        session.delete(film_price)
        session.commit()
        return jsonify({"message": "Film price deleted successfully"})

# CRUD для налоговых ставок
@app.route('/tax_rates', methods=['POST'])
def create_tax_rate():
    try:
        data = TaxRateRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        new_tax_rate = TaxRate(country=data.country, name=data.name, rate=data.rate)
        session.add(new_tax_rate)
        session.commit()
        return jsonify({"message": "Tax rate created successfully", "id": new_tax_rate.id}), 201

@app.route('/tax_rates/<string:country>', methods=['GET'])
def get_tax_rate(country):
    with SessionLocal() as session:
        tax_rate = session.query(TaxRate).filter(TaxRate.country == country).first()
        if not tax_rate:
            return jsonify({"error": "Tax rate not found"}), 404
        return jsonify({"country": tax_rate.country, "name": tax_rate.name, "rate": tax_rate.rate})

@app.route('/tax_rates/<string:country>', methods=['PUT'])
def update_tax_rate(country):
    try:
        data = TaxRateRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        tax_rate = session.query(TaxRate).filter(TaxRate.country == country).first()
        if not tax_rate:
            return jsonify({"error": "Tax rate not found"}), 404
        tax_rate.name = data.name
        tax_rate.rate = data.rate
        session.commit()
        return jsonify({"message": "Tax rate updated successfully"})

@app.route('/tax_rates/<string:country>', methods=['DELETE'])
def delete_tax_rate(country):
    with SessionLocal() as session:
        tax_rate = session.query(TaxRate).filter(TaxRate.country == country).first()
        if not tax_rate:
            return jsonify({"error": "Tax rate not found"}), 404
        session.delete(tax_rate)
        session.commit()
        return jsonify({"message": "Tax rate deleted successfully"})

# CRUD для скидок
@app.route('/discounts', methods=['POST'])
def create_discount():
    try:
        data = DiscountRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        new_discount = Discount(
            item_id=data.item_id,
            name=data.name,
            type=data.type,
            value=data.value,
            start_date=data.start_date,
            end_date=data.end_date
        )
        session.add(new_discount)
        session.commit()
        return jsonify({"message": "Discount created successfully", "id": new_discount.id}), 201

@app.route('/discounts/<uuid:id>', methods=['GET'])
def get_discount(id):
    with SessionLocal() as session:
        discount = session.query(Discount).filter(Discount.id == id).first()
        if not discount:
            return jsonify({"error": "Discount not found"}), 404
        return jsonify({"id": discount.id, "item_id": discount.item_id, "name": discount.name, "type": discount.type, "value": discount.value, "start_date": discount.start_date, "end_date": discount.end_date})

@app.route('/discounts/<uuid:id>', methods=['PUT'])
def update_discount(id):
    try:
        data = DiscountRequest.model_validate(request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    with SessionLocal() as session:
        discount = session.query(Discount).filter(Discount.id == id).first()
        if not discount:
            return jsonify({"error": "Discount not found"}), 404
        discount.name = data.name
        discount.type = data.type
        discount.value = data.value
        discount.start_date = data.start_date
        discount.end_date = data.end_date
        session.commit()
        return jsonify({"message": "Discount updated successfully"})

@app.route('/discounts/<uuid:id>', methods=['DELETE'])
def delete_discount(id):
    with SessionLocal() as session:
        discount = session.query(Discount).filter(Discount.id == id).first()
        if not discount:
            return jsonify({"error": "Discount not found"}), 404
        session.delete(discount)
        session.commit()
        return jsonify({"message": "Discount deleted successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)