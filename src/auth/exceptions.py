import fastapi_jsonrpc as jsonrpc
from fastapi_users.router import ErrorCode
from pydantic import BaseModel


class UserAlreadyExists(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = ErrorCode.REGISTER_USER_ALREADY_EXISTS


class InvalidPassword(jsonrpc.BaseError):
    code = 5001
    MESSAGE = ErrorCode.REGISTER_INVALID_PASSWORD

    class DataModel(BaseModel):
        reason: str


class InvalidAuthenticate(jsonrpc.BaseError):
    code = 5002
    MESSAGE = "Invalid authentication"

    class DataModel(BaseModel):
        reason: str


class LoginBadCredentials(jsonrpc.BaseError):
    CODE = 5003
    MESSAGE = ErrorCode.LOGIN_BAD_CREDENTIALS
