import uuid
from datetime import datetime
from typing import List

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, GUID, UUID_ID
from sqlalchemy import (JSON, TIMESTAMP, Boolean, Column, ForeignKey, Integer,
                        String, Table)

# from database import metadata
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    videos: Mapped[List["Video"]] = relationship("Video", back_populates="user", lazy="selectin")
    liked_videos: Mapped[List["Like"]] = relationship("Video", secondary="like",
                                                      primaryjoin="and_(User.id==Like.user_id, Like.status)",
                                                      back_populates="liked_users", lazy="selectin")
    disliked_videos: Mapped[List["Like"]] = relationship("Video", secondary="like",
                                                         primaryjoin="and_(User.id==Like.user_id, Like.status==False)",
                                                         back_populates="disliked_users", lazy="selectin")
