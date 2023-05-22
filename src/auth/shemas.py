import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr, BaseModel


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: uuid.UUID
    name: str
    email: str
    username: str
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(schemas.BaseUserCreate):
    name: str
    username: str
    email: EmailStr
    password: str
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserLogin(BaseModel):
    username: str
    password: str
