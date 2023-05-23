import uuid
from datetime import datetime

from fastapi_users_db_sqlalchemy import UUID_ID, GUID
from sqlalchemy import Boolean, ForeignKey, TIMESTAMP, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"))
    video_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("video.id"))
    posted_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    edited_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=True)
