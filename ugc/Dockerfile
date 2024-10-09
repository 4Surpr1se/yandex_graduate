FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn gevent

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--worker-class", "gevent", "app:app"]
