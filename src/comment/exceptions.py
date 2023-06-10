import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class InvalidComment(jsonrpc.BaseError):
    CODE = 8000
    MESSAGE = "Invalid comment"

    class DataModel(BaseModel):
        reason: str


class NonExistentComment(jsonrpc.BaseError):
    CODE = 7001
    MESSAGE = "Comment does not exist"

