from flask import Flask, jsonify, request
from pydantic import ValidationError
from config import SessionLocal
from sqlalchemy.orm import Session
from models import FilmPrice, Subscription
from services import calculate_price
from request_models import FilmPriceRequest, SubscriptionPriceRequest 

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)