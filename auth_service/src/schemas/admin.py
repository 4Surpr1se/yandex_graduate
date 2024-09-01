from pydantic import BaseModel
from uuid import UUID


class RoleResponse(BaseModel):
    success: bool
    message: str
    user_id: UUID
    role: str
