from fastapi import APIRouter, HTTPException, Depends
from src.schemas.notification import Notification
from src.services.notifications import NotificationService
from src.db.base import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/send-notification")
async def send_notification(notification: Notification, db: AsyncSession = Depends(get_session)):
    service = NotificationService(db)
    service.send_notification_to_queue(notification)
    await service.add_notification(notification)
    return {"status": "Notification added successfully"}
