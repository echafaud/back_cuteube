import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class SubscribeException(jsonrpc.BaseError):
    CODE = 10000
    MESSAGE = "Failed to subscribe"

    class DataModel(BaseModel):
        reason: str


class UnSubscribeException(jsonrpc.BaseError):
    CODE = 10001
    MESSAGE = "Failed to unsubscribe"

    class DataModel(BaseModel):
        reason: str


class NonExistentSubscription(jsonrpc.BaseError):
    CODE = 10002
    MESSAGE = "Subscription does not exist"
