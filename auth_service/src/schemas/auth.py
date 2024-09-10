from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    login: str | None = None

class UserAuth(BaseModel):
    login: str
    password: str