import uuid

from pydantic import BaseModel
from pydantic.schema import date


class BaseComment(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentCreate(BaseComment):
    video_id: uuid.UUID


class CommentRead(CommentCreate):
    id: uuid.UUID
    owner_id: uuid.UUID
    posted_at: date
    edited_at: date | None


class CommentEdit(BaseComment):
    id: uuid.UUID
