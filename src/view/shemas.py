import uuid
from datetime import timedelta

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import INTERVAL


class BaseView(BaseModel):
    video_id: uuid.UUID
    stop_timecode: timedelta
    viewing_time: timedelta | None

    class Config:
        orm_mode = True


class ViewRead(BaseView):
    id: uuid.UUID
    # fingerprint: str
    author_id: uuid.UUID | None

    def create_user_view_dict(self):
        return self.dict(
            include={
                'id': True,
                'author_id': True,
                'video_id': True,
            },
        )


class ViewRemove(BaseModel):
    video_id: uuid.UUID
