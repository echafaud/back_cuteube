from uuid import UUID as pyUUID
from sqlalchemy import ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Subscription(Base):
    __tablename__ = "subscription"
    subscriber: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"), primary_key=True)
    subscribed: Mapped[pyUUID] = mapped_column(UUID, ForeignKey("user.id"), primary_key=True)
