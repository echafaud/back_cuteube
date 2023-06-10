import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class UploadVideoException(jsonrpc.BaseError):
    CODE = 6000
    MESSAGE = "Upload video exception"

    class DataModel(BaseModel):
        reason: str


class NonExistentVideo(jsonrpc.BaseError):
    CODE = 6001
    MESSAGE = "Video does not exist"


class DeleteVideoException(jsonrpc.BaseError):
    CODE = 6002
    MESSAGE = "Failed to delete files from s3"
