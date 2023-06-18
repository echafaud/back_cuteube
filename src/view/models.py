import uuid
from datetime import datetime
from uuid import UUID as pyUUID
from sqlalchemy import Boolean, ForeignKey, TIMESTAMP, String, UUID
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import mapped_column, Mapped, relationship, backref

from src.database import Base


class View(Base):
    __tablename__ = "view"
    id: Mapped[pyUUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    fingerprint: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"), nullable=True)
    video_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("video.id", ondelete='CASCADE'))
    stop_timecode: Mapped[INTERVAL] = mapped_column(INTERVAL)
    viewing_time: Mapped[INTERVAL] = mapped_column(INTERVAL, nullable=True)
    viewed_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    video: Mapped["Video"] = relationship('Video',
                                          backref=backref('models_views', passive_deletes=True, lazy="dynamic"))


class UserView(Base):
    __tablename__ = "user_view"
    owner_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"), primary_key=True)
    video_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("video.id", ondelete='CASCADE'), primary_key=True)
    view_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("view.id"))
    video: Mapped["Video"] = relationship('Video',
                                          backref=backref('models_user_views', passive_deletes=True, lazy="dynamic"))
