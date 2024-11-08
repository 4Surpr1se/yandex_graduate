from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import requests
from jinja2 import Template
from uuid import uuid4

app = FastAPI()

templates = Jinja2Templates(directory="templates")

API_URL = "http://notification_api:8000/api/notifications/send-notification"


class MassMailRequest(BaseModel):
    title: str
    body_template: str
    recipients: List[str]
    usernames: Optional[List[str]] = None
    channel_type: int = 1
    message_type: int = 1


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/admin/send-mass-mail")
async def send_mass_mail(request: MassMailRequest):
    try:
        request_data = {
            "title": request.title,
            "body": request.body_template,
            "channel_type": request.channel_type,
            "message_type": request.message_type,
            "recipients": request.recipients,
            "usernames": request.usernames or ["User" for _ in request.recipients]
        }

        headers = {
            "Content-Type": "application/json",
            "X-Request-Id": str(uuid4())
        }

        response = requests.post(API_URL, json=request_data, headers=headers)
        response.raise_for_status()

        return {"status": "success", "detail": "Уведомления отправлены."}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке уведомлений: {e}")
