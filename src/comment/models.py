import uuid
from uuid import UUID as pyUUID
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, TIMESTAMP, String, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship, backref

from src.database import Base


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[pyUUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(length=5000), nullable=False)
    owner_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"))
    video_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("video.id", ondelete='CASCADE'))
    posted_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    edited_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)

    video: Mapped["Video"] = relationship('Video', backref=backref('comments', passive_deletes=True, lazy="dynamic"))
