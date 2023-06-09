import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class UploadVideoException(jsonrpc.BaseError):
    CODE = 6000
    MESSAGE = "Upload video exception"

    class DataModel(BaseModel):
        reason: str


class VideoNotExists(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = "Video not exists"


class DeleteVideoException(jsonrpc.BaseError):
    CODE = 5001
    MESSAGE = "Failed to delete files from s3"
