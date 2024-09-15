from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from core.config import settings
from typing import Optional
import requests

security = HTTPBearer()

async def verify_jwt(request: Request):
    token: Optional[str] = request.cookies.get('access_token')
    refresh_token: Optional[str] = request.cookies.get('refresh_token')

    x_request_id = request.headers.get("X-Request-Id", "")
    
    headers = {
        "Cookie": request.headers.get("cookie"),
        "X-Request-Id": x_request_id 
    }
    if not token and refresh_token:
        new_tokens = await refresh_access_token(headers)
        if new_tokens:
            token = new_tokens.get("access_token")
            request.cookies["access_token"] = token
            headers["Cookie"] = f'access_token={token}; refresh_token={refresh_token}'
        else:
            raise HTTPException(status_code=401, detail="Unable to refresh access token")

    if token:
        auth_service_url = f"{settings.auth_service_url}/api/auth/verify_token"
        response = requests.post(auth_service_url, json={"token": token}, headers=headers)
        
        if response.status_code == 401 and refresh_token:
            new_tokens = await refresh_access_token(headers)
            if new_tokens:
                token = new_tokens.get("access_token")
                request.cookies["access_token"] = token
                headers["Cookie"] = f'access_token={token}; refresh_token={refresh_token}'
                response = requests.post(auth_service_url, json={"token": token}, headers=headers)
        
        if response.status_code != 200:
            try:
                detail = response.json().get("detail", "Unauthorized")
            except ValueError:
                detail = "Unauthorized"
            raise HTTPException(status_code=401, detail=detail)
        
        return response.json()
    
    raise HTTPException(status_code=401, detail="No access token and refresh token provided")

async def refresh_access_token(headers: dict):
    refresh_url = f"{settings.auth_service_url}/api/auth/refresh"
    refresh_response = requests.post(refresh_url, headers=headers)

    if refresh_response.status_code == 200:
        return refresh_response.json()
    return None
