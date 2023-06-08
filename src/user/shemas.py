import uuid
from typing import Optional
from pydantic import EmailStr, BaseModel


class CreateUpdateDictModel(BaseModel):
    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class UserRead(CreateUpdateDictModel):
    id: uuid.UUID
    name: str
    email: str
    username: str
    count_subscribers: int = 0
    is_subscribed: bool | None = None
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        orm_mode = True


class UserCreate(CreateUpdateDictModel):
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


class UserLoginRead(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    username: str
    count_subscribers: int = 0
    is_active: bool = False
    is_superuser: bool = False
    is_verified: bool = False
