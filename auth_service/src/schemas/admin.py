from uuid import UUID

from pydantic import BaseModel


class RoleResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID = None
    role: str = None
