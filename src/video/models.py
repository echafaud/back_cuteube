import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import GUID, UUID_ID
from sqlalchemy import String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base


class Video(Base):
    __tablename__ = "video"
    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(length=60), nullable=False)
    description: Mapped[str] = mapped_column(String(length=340), nullable=False)
    upload_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    author: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"))

    comments: Mapped[List["Comment"]] = relationship("Comment", backref="comments", lazy="selectin")
    user: Mapped["User"] = relationship("User", back_populates="videos", lazy="selectin")
    liked_users: Mapped[List["User"]] = relationship("User", secondary="like",
                                                     primaryjoin="and_(Video.id == Like.video_id, Like.status)",
                                                     back_populates="liked_videos",
                                                     lazy="selectin")
    disliked_users: Mapped[List["User"]] = relationship("User", secondary="like",
                                                        primaryjoin="and_(Video.id == Like.video_id, Like.status == False)",
                                                        back_populates="disliked_videos",
                                                        lazy="selectin")
    viewed_users: Mapped[List["User"]] = relationship("User", back_populates="viewed_videos",
                                                      primaryjoin="Video.id==UserView.video_id",
                                                      secondary="user_view", lazy="selectin")
