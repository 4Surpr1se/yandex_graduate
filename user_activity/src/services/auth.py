from typing import Optional
import requests
from fastapi import Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer
from src.core.config import settings

security = HTTPBearer()


async def verify_jwt(request: Request, response: Response):
    access_token: Optional[str] = request.cookies.get('access_token')
    refresh_token: Optional[str] = request.cookies.get('refresh_token')

    headers = {
        "Cookie": request.headers.get("cookie"),
        "X-Request-Id": request.headers.get("X-Request-Id", "")
    }

    if not access_token and refresh_token:
        tokens = await refresh_access_token(headers)
        if tokens:
            access_token = tokens.get("access_token")
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                max_age=tokens.get("access_token_expires_in", settings.access_token_expire_minutes * 60)
            )

    if access_token:
        try:
            auth_response = requests.post(
                f"{settings.auth_service_url}/api/auth/verify_token",
                json={"token": access_token},
                headers=headers
            )
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        if auth_response.status_code == 200:
            return auth_response.json()

        elif auth_response.status_code == 401 and refresh_token:
            tokens = await refresh_access_token(headers)
            if tokens:
                new_access_token = tokens.get("access_token")
                new_refresh_token = tokens.get("refresh_token")

                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    max_age=tokens.get("access_token_expires_in", settings.access_token_expire_minutes * 60)
                )
                if new_refresh_token:
                    response.set_cookie(
                        key="refresh_token",
                        value=new_refresh_token,
                        httponly=True,
                        max_age=tokens.get("refresh_token_expires_in",
                                           settings.refresh_token_expire_days * 24 * 60 * 60)
                    )
                return tokens

    raise HTTPException(status_code=401, detail="Unauthorized")


async def refresh_access_token(headers: dict):
    refresh_url = f"{settings.auth_service_url}/api/auth/refresh"
    try:
        refresh_response = requests.post(refresh_url, headers=headers)
    except requests.exceptions.RequestException:
        return None

    if refresh_response.status_code == 401:
        detail = refresh_response.json().get("detail", "Unauthorized")
        if detail.lower() == "invalid login or password":
            raise HTTPException(status_code=401, detail="Invalid login or password")

    if refresh_response.status_code == 200:
        return refresh_response.json()

    return None
