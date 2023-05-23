import uuid

from pydantic import BaseModel


class BaseLike(BaseModel):
    status: bool
    video_id: uuid.UUID

    class Config:
        orm_mode = True
