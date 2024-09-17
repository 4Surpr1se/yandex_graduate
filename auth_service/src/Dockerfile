# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# only for oauth testing
#ENV OAUTHLIB_INSECURE_TRANSPORT=1

# Устанавливаем рабочую директорию
WORKDIR /auth

# Копируем файл зависимостей
COPY auth_service/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY auth_service/. .

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска FastAPI с использованием Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
