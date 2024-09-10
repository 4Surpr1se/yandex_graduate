from uuid import UUID

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.config import settings
from src.models.role import Role
from src.models.user import User
from src.schemas.admin import RoleResponse


class RolesService:

    async def validate_and_fetch(self, user_id: UUID, role: str, access_token: str, db: AsyncSession):
        access = await self.check_permissions(access_token)
        if not access:
            return None, None, None

        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.unique().scalar_one_or_none()
        if not user:
            return None, None, None

        role_result = await db.execute(select(Role).where(Role.name == role))
        existing_role = role_result.scalar_one_or_none()
        if not existing_role:
            return None, None, None

        return user, existing_role, access

    async def add_role(self, user_id: UUID, role: str, access_token: str, db: AsyncSession):
        user, existing_role, access = await self.validate_and_fetch(user_id, role, access_token, db)
        if not user or existing_role in user.roles:
            return None

        user.roles.append(existing_role)
        await db.commit()
        return RoleResponse(
            success=True,
            message=f"Role '{role}' successfully added to user with ID {user_id}.",
            user_id=user_id,
            role=role
        )

    async def remove_role(self, user_id: UUID, role: str, access_token: str, db: AsyncSession):
        user, existing_role, access = await self.validate_and_fetch(user_id, role, access_token, db)
        if not user:
            return None
        if not existing_role:
            return RoleResponse(
                success=False,
                message=f"User with ID {user_id} doesn't have role '{role}'.",
                user_id=user_id,
                role=role
            )
        if existing_role in user.roles:
            user.roles.remove(existing_role)
            await db.commit()
            return RoleResponse(
                success=True,
                message=f"Role '{role}' successfully removed from user with ID {user_id}.",
                user_id=user_id,
                role=role
            )
        return None

    async def check_permissions(self, access_token: str):
        try:
            payload = jwt.decode(access_token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            roles = payload.get('roles', [])
            return 'admin' in roles or 'super_admin' in roles
        except JWTError:
            return False


def get_roles_service():
    return RolesService()
