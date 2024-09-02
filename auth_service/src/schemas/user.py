from uuid import UUID
from typing import List

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
