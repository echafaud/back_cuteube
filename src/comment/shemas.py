import uuid

from pydantic import BaseModel


class BaseComment(BaseModel):
    text: str

    class Config:
        orm_mode = True


class CommentCreate(BaseComment):
    video_id: uuid.UUID


class CommentRead(CommentCreate):
    author_id: uuid.UUID


class CommentEdit(BaseComment):
    id: uuid.UUID


class CommentRemove(BaseModel):
    id: uuid.UUID
