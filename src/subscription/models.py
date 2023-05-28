from fastapi_users_db_sqlalchemy import UUID_ID, GUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Subscription(Base):
    __tablename__ = "subscription"
    subscriber: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), primary_key=True)
    subscribed: Mapped[UUID_ID] = mapped_column(GUID, ForeignKey("user.id"), primary_key=True)
