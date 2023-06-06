import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, GUID, UUID_ID
from sqlalchemy import (TIMESTAMP, Boolean, String)
# from database import metadata
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from src.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    id: Mapped[UUID_ID] = mapped_column(GUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    username: Mapped[str] = mapped_column(String(length=20), unique=True, index=True, nullable=False)
    registered_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    email: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    posted_comments: Mapped[List["Comment"]] = relationship("Comment", backref="posted_comments", lazy="dynamic")
    videos: Mapped[List["Video"]] = relationship("Video", back_populates="user", lazy="dynamic")
    liked_videos: Mapped[List["Video"]] = relationship("Video", secondary="like",
                                                       primaryjoin="and_(User.id==Like.user_id, Like.status)",
                                                       back_populates="liked_users", lazy="dynamic")
    disliked_videos: Mapped[List["Video"]] = relationship("Video", secondary="like",
                                                          primaryjoin="and_(User.id==Like.user_id, Like.status==False)",
                                                          back_populates="disliked_users", lazy="dynamic")
    viewed_videos: Mapped[List["Video"]] = relationship("Video", back_populates="viewed_users",
                                                        primaryjoin="User.id==UserView.author_id",
                                                        secondary="user_view", lazy="dynamic")
    subscribers: Mapped[List["User"]] = relationship("User",
                                                     primaryjoin="User.id==Subscription.subscribed",
                                                     secondaryjoin="User.id==Subscription.subscriber",
                                                     backref=backref("subscribed", lazy="dynamic"),
                                                     secondary="subscription", lazy="dynamic",)
    # subscribers: Mapped[List["User"]] = relationship("User", secondary="subscription", lazy="selectin",
    #                                                  back_populates="subscribers",
    #                                                  foreign_keys="Subscription.subscriber",
    #                                                  primaryjoin="User.id==Subscription.subscriber")
