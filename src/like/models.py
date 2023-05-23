from fastapi_users_db_sqlalchemy import UUID_ID, GUID
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.database import Base


class Like(Base):
    __tablename__ = "like"
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), primary_key=True)
    video_id: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("video.id"), primary_key=True)

    # user: Mapped["User"] = relationship(back_populates="likes", lazy="selectin")
    # video: Mapped["Video"] = relationship(back_populates="likes", lazy="selectin")
