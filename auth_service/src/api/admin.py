from fastapi import APIRouter, Depends, HTTPException, Request
from http import HTTPStatus
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.user import UserRoleRequest
from src.services.roles import get_roles_service, RolesService
from src.db.postgres import get_session

router = APIRouter()


@router.post("/{user_id}/add-role/", status_code=HTTPStatus.OK)
async def add_roles(user_id: UUID,
                    user_role_request: UserRoleRequest,
                    request: Request,
                    roles_service: RolesService = Depends(get_roles_service),
                    db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing session token")

    res = await roles_service.add_role(user_id, user_role_request.role, access_token, db)
    if not res:
        raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                            detail='Not enough permissions or invalid role')
    return res


@router.post("/{user_id}/remove-role/", status_code=HTTPStatus.OK)
async def remove_roles(user_id: UUID,
                       user_role_request: UserRoleRequest,
                       request: Request,
                       roles_service: RolesService = Depends(get_roles_service),
                       db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Missing session token")

    res = await roles_service.remove_role(user_id, user_role_request.role, access_token, db)
    if not res:
        raise HTTPException(status_code=HTTPStatus.METHOD_NOT_ALLOWED,
                            detail='Not enough permissions or invalid role')
    return res
