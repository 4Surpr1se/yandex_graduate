FROM python:3.12

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]
