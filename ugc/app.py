import logging
import asyncio
from flask import Flask, jsonify, request
from config import settings
from kafka_producer import create_topics, kafka_producer

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

with app.app_context():
    create_topics()


async def async_send_message(topic, key, value):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, kafka_producer.send_message, topic, key, value)


@app.route('/click', methods=['POST'])
async def track_click():
    data = request.json
    if not data or 'user_id' not in data or 'element' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    success = await async_send_message(settings.kafka_clicks_topic, data['user_id'], data)

    if not success:
        return jsonify({'error': 'Kafka service is unavailable, try again later'}), 503

    return jsonify({'status': 'click event tracked'})


@app.route('/page_view', methods=['POST'])
async def track_page_view():
    data = request.json
    if not data or 'user_id' not in data or 'page' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    success = await async_send_message(settings.kafka_page_views_topic, data['user_id'], data)

    if not success:
        return jsonify({'error': 'Kafka service is unavailable, try again later'}), 503

    return jsonify({'status': 'page view event tracked'})

@app.route('/custom_event', methods=['POST'])
async def track_custom_event():
    try:
        data = request.json
        if not data or 'user_id' not in data or 'event_name' not in data:
            app.logger.error("Invalid request data")
            return jsonify({'error': 'Invalid request'}), 400

        success = await async_send_message(settings.kafka_custom_events_topic, str(data['user_id']), data)

        if not success:
            app.logger.error("Failed to send message to Kafka")
            return jsonify({'error': 'Kafka service is unavailable, try again later'}), 503

        return jsonify({'status': 'custom event tracked'})
    except Exception as e:
        app.logger.error(f"Error while processing custom_event: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host=settings.flask_host, port=settings.flask_port)
