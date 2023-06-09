import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import GUID, UUID_ID
from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base


class Video(Base):
    __tablename__ = "video"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(length=100), nullable=False)
    description: Mapped[str] = mapped_column(String(length=5000), nullable=False)
    upload_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    author: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"))
    duration: Mapped[INTERVAL] = mapped_column(INTERVAL)

    # comments: Mapped[List["Comment"]] = relationship("Comment", backref="comments", lazy="dynamic")
    user: Mapped["User"] = relationship("User", back_populates="videos", )
    liked_users: Mapped[List["User"]] = relationship("User", secondary="like",
                                                     primaryjoin="and_(Video.id == Like.video_id, Like.status)",
                                                     back_populates="liked_videos",
                                                     lazy="dynamic")
    disliked_users: Mapped[List["User"]] = relationship("User", secondary="like",
                                                        primaryjoin="and_(Video.id == Like.video_id, Like.status == False)",
                                                        back_populates="disliked_videos",
                                                        lazy="dynamic")
    viewed_users: Mapped[List["User"]] = relationship("User", back_populates="viewed_videos",
                                                      primaryjoin="Video.id==UserView.video_id",
                                                      secondary="user_view", lazy="dynamic")
