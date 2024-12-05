from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_session
from src.schemas.user import UserRoleRequest
from src.services.roles import RolesService, get_roles_service

router = APIRouter()


@router.post("/{user_id}/add-role/", status_code=HTTPStatus.OK)
async def add_roles(user_id: UUID,
                    user_role_request: UserRoleRequest,
                    request: Request,
                    roles_service: RolesService = Depends(get_roles_service),
                    db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")

    res = await roles_service.add_role(user_id, user_role_request.role, access_token, db)
    if not res.user_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='User doesn\'t exist')
    if not res.success:
        return res
    if not res:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail='Not enough permissions or invalid role')
    return res


@router.post("/{user_id}/remove-role/", status_code=HTTPStatus.OK)
async def remove_roles(user_id: UUID,
                       user_role_request: UserRoleRequest,
                       request: Request,
                       roles_service: RolesService = Depends(get_roles_service),
                       db: AsyncSession = Depends(get_session)):
    access_token = request.cookies.get("access_token")

    res = await roles_service.remove_role(user_id, user_role_request.role, access_token, db)
    if not res.user_id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail='User doesn\'t exist')
    if not res.success:
        return res
    if not res:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN,
                            detail='Not enough permissions or invalid role')
    return res
