import uuid

from fastapi import Form, UploadFile, File
from pydantic import BaseModel, PrivateAttr

from src.auth.models import User


# class CreateUpdateDictModel(BaseModel):
#     def create_update_dict(self):
#         return self.dict(
#             exclude_unset=True,
#             exclude={
#                 "id",
#                 "upload_at"
#             },
#         )


class BaseVideo(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True


class VideoUpload(BaseVideo):
    _video_file: File = PrivateAttr()
    _preview_file: File = PrivateAttr()

    # file: UploadFile
    # upload_at
    # author: uuid.UUID

    def __init__(self, title: str = Form(...), description: str = Form(...), video_file: UploadFile = File(...),
                 preview_file: UploadFile = File(...)):
        super().__init__(**{"title": title, "description": description})
        # self.title = title
        # self.description = description
        self._video_file = video_file
        self._preview_file = preview_file


class VideoView(BaseVideo):
    id: uuid.UUID
