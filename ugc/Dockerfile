FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV FLASK_APP=app.py

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--worker-class", "gevent", "app:app"]
