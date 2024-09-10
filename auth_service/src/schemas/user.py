from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True


class UserRoleRequest(BaseModel):
    role: str


class UpdateResponse(BaseModel):
    success: bool
    message: str

class UserLoginScheme(BaseModel):
    id: UUID
    logged_at: datetime

    class Config:
        orm_mode = True