from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from google_auth_oauthlib.flow import Flow as GoogleFlow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.db.postgres import get_session
from src.models.login_history import Provider, UserSignIn
from src.models.social_account import UserSocialAccount
from src.services.auth import create_tokens
from src.services.user import create_user_service, get_user_by_login

router = APIRouter()

PROVIDER_SETTINGS = {
    "google": {
        "flow": GoogleFlow.from_client_secrets_file(
            settings.google_secret_file_path,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri=f'{settings.nginx_url}/api/auth/google/callback',
        ),
        "id_token_verifier": google_id_token.verify_oauth2_token,
        "provider_enum": Provider.GOOGLE,
    }
}

def get_oauth_flow(provider: str):
    if provider not in PROVIDER_SETTINGS:
        raise HTTPException(status_code=400, detail="Unknown provider")
    return PROVIDER_SETTINGS[provider]["flow"]

def get_id_token_verifier(provider: str):
    if provider not in PROVIDER_SETTINGS:
        raise HTTPException(status_code=400, detail="Unknown provider")
    return PROVIDER_SETTINGS[provider]["id_token_verifier"]

def get_provider_enum(provider: str):
    if provider not in PROVIDER_SETTINGS:
        raise HTTPException(status_code=400, detail="Unknown provider")
    return PROVIDER_SETTINGS[provider]["provider_enum"]

@router.get("/login")
async def login(provider: str = Query(...)):
    flow = get_oauth_flow(provider)
    authorization_url, state = flow.authorization_url(prompt='consent')
    return RedirectResponse(url=authorization_url)

@router.get("/callback")
async def auth_callback(request: Request, provider: str = Query(...), db: AsyncSession = Depends(get_session)):
    try:
        flow = get_oauth_flow(provider)
        flow.fetch_token(authorization_response=str(request.url))

        credentials = flow.credentials
        id_token_verifier = get_id_token_verifier(provider)
        user_info = id_token_verifier(credentials.id_token, google_requests.Request(), settings.google_client_id)

        user = await get_user_by_login(user_info['email'], db)

        if not user:
            user = await create_user_service(user_info, db)

        existing_account = await db.execute(
            select(UserSocialAccount).where(
                UserSocialAccount.user_id == user.id,
                UserSocialAccount.provider == provider,
                UserSocialAccount.social_id == user_info['sub']
            )
        )

        if not existing_account.scalars().first():
            social_account = UserSocialAccount(
                user_id=user.id,
                provider=provider,
                social_id=user_info['sub']
            )
            db.add(social_account)
            await db.commit()
            await db.refresh(social_account)

        tokens = await create_tokens(user, db)

        user_login = UserSignIn(user_id = user.id, provider=Provider.GOOGLE)
        db.add(user_login)
        await db.commit()
        await db.refresh(user_login)

        response = RedirectResponse(url='/')
        response.set_cookie(key="access_token", value=tokens.access_token, httponly=True, max_age=60 * settings.access_token_expire_minutes)
        response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True, max_age=60 * 60 * 24 * settings.refresh_token_expire_days)

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))