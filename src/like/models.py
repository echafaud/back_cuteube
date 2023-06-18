from sqlalchemy import Boolean, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship, backref
from uuid import UUID as pyUUID
from src.database import Base


class Like(Base):
    __tablename__ = "like"
    status: Mapped[bool] = mapped_column(Boolean, nullable=False)
    owner_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"), primary_key=True)
    video_id: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("video.id", ondelete='CASCADE'), primary_key=True)

    video: Mapped["Video"] = relationship('Video',
                                          backref=backref('models_likes', passive_deletes=True, lazy="dynamic"))

    # user: Mapped["User"] = relationship(back_populates="likes", lazy="selectin")
    # video: Mapped["Video"] = relationship(back_populates="likes", lazy="selectin")
