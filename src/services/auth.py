from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from core.config import settings
from typing import Optional
import requests

security = HTTPBearer()

async def verify_jwt(request: Request):
    token: Optional[str] = request.cookies.get('access_token')
    
    if not token:
        raise HTTPException(status_code=401, detail="No access token provided")
    
    headers = {"Cookie": request.headers.get("cookie")}

    auth_service_url = f"{settings.auth_service_url}/api/auth/verify_token"
    response = requests.post(auth_service_url, json={"token": token}, headers=headers)
    
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", "Unauthorized")
        except ValueError:
            detail = "Unauthorized"
        
        raise HTTPException(status_code=401, detail=detail)
    
    return response.json()