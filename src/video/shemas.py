import uuid

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, PrivateAttr
from pydantic.schema import timedelta, date

from src.video.models import Permission


class BaseVideo(BaseModel):
    title: str
    description: str
    permission: str

    class Config:
        orm_mode = True


class VideoUpload(BaseVideo):
    _video_file: File = PrivateAttr()
    _preview_file: File = PrivateAttr()

    # file: UploadFile
    # upload_at
    # author: uuid.UUID

    def __init__(self, title: str = Form(...),
                 description: str = Form(...),
                 permission: str = Form(...),
                 video_file: UploadFile = File(...),
                 preview_file: UploadFile = File(...)):
        super().__init__(**{"title": title, "description": description, 'permission': permission})
        # self.title = title
        # self.description = description
        self._video_file = video_file
        self._preview_file = preview_file


class VideoView(BaseVideo):
    id: uuid.UUID
    owner: uuid.UUID
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    like: bool | None
    permission: str
    stop_timecode: timedelta = 0
    uploaded_at: date

