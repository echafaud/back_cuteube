import uuid

from pydantic import BaseModel


class BaseSubscription(BaseModel):
    subscribed: uuid.UUID
