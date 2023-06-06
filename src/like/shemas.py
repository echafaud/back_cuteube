import uuid

from pydantic import BaseModel


class BaseLike(BaseModel):
    status: bool | None
    video_id: uuid.UUID

    class Config:
        orm_mode = True
