import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.postgres import get_session
from src.models.login_history import Provider, UserSignIn
from src.services.auth import create_tokens
from src.services.user import create_user_service, get_user_by_login

logger = logging.getLogger(__name__)
router = APIRouter()


flow = Flow.from_client_secrets_file(
    settings.google_secret_file_path,
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri=f'{settings.nginx_url}/api/google/callback',
)

@router.get("/login")
async def login():
    authorization_url, state = flow.authorization_url(prompt='consent')
    return RedirectResponse(url=authorization_url)

@router.get("/callback")
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_session)):
    try:
        flow.fetch_token(authorization_response=str(request.url))

        credentials = flow.credentials
        user_info = id_token.verify_oauth2_token(
            credentials.id_token, 
            requests.Request(), 
            settings.google_client_id
        )

        user = await get_user_by_login(user_info['email'], db)
        if not user:
            user = await create_user_service(user_info, db)

        tokens = await create_tokens(user, db)

        user_agent = request.headers.get('User-Agent', 'unknown')
        if 'Smart' in user_agent:
            device_type = 'smart'
        elif 'Mobile' in user_agent:
            device_type = 'mobile'
        else:
            device_type = 'web'

        user_sign_in = UserSignIn(user_id=user.id, user_device_type=device_type, provider=Provider.GOOGLE)
        db.add(user_sign_in)
        await db.commit()
        await db.refresh(user_sign_in)

        response = RedirectResponse(url='/')
        response.set_cookie(key="access_token", value=tokens.access_token, httponly=True, max_age=60 * settings.access_token_expire_minutes)
        response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, max_age=60 * 60 * 24 * settings.refresh_token_expire_days)

        return response
    except Exception as e:
        logger.error(f'Google auth failed with exception: {e}')
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e))