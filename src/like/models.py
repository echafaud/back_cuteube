from fastapi_users_db_sqlalchemy import UUID_ID, GUID
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, backref

from src.database import Base


class Like(Base):
    __tablename__ = "like"
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), primary_key=True)
    video_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("video.id", ondelete='CASCADE'), primary_key=True)

    video: Mapped["Video"] = relationship('Video', backref=backref('models_likes', passive_deletes=True, lazy="dynamic"))

    # user: Mapped["User"] = relationship(back_populates="likes", lazy="selectin")
    # video: Mapped["Video"] = relationship(back_populates="likes", lazy="selectin")
