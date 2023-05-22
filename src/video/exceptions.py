import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class UploadVideoException(jsonrpc.BaseError):
    code = 5002
    MESSAGE = "UploadVideoException"

    class DataModel(BaseModel):
        reason: str


class VideoNotExists(jsonrpc.BaseError):
    code = 5002
    MESSAGE = "VideoNotExists"
