import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class ViewRecordException(jsonrpc.BaseError):
    CODE = 9000
    MESSAGE = "Something went wrong when recording the view"


class LimitViewException(jsonrpc.BaseError):
    CODE = 9001
    MESSAGE = "Limit of views has been reached"


class InvalidView(jsonrpc.BaseError):
    CODE = 9002
    MESSAGE = "Invalid view"

    class DataModel(BaseModel):
        reason: str


class NonExistentView(jsonrpc.BaseError):
    CODE = 9003
    MESSAGE = "View does not exist"
