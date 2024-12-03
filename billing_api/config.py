import os


class Settings:
    # URL для price_service и billing_service
    price_service_url: str = os.getenv("PRICE_SERVICE_URL", "http://price_service:5005")
    billing_service_url: str = os.getenv("BILLING_SERVICE_URL", "http://billing_service:8009")

settings = Settings()
