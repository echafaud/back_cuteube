import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import UUID_ID, GUID
from sqlalchemy import Boolean, ForeignKey, TIMESTAMP, String
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base


class View(Base):
    __tablename__ = "view"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    # fingervprint: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), nullable=True)
    video_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("video.id"))
    stop_timecode: Mapped[INTERVAL] = mapped_column(INTERVAL)
    viewing_time: Mapped[INTERVAL] = mapped_column(INTERVAL, nullable=True)
    viewed_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)


class UserView(Base):
    __tablename__ = "user_view"
    author_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), primary_key=True)
    video_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("video.id"), primary_key=True)
    view_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("view.id"))
