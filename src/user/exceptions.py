import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel


class UserAlreadyExists(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = "User already exists"


class InvalidPassword(jsonrpc.BaseError):
    CODE = 5001
    MESSAGE = "Register invalid password"

    class DataModel(BaseModel):
        reason: str


class LoginBadCredentials(jsonrpc.BaseError):
    CODE = 5002
    MESSAGE = "Login bad credentials"


class InvalidField(jsonrpc.BaseError):
    CODE = 5003
    MESSAGE = "Invalid field"

    class DataModel(BaseModel):
        details: str


class InvalidAuthenticate(jsonrpc.BaseError):
    CODE = 5004
    MESSAGE = "Invalid authentication"

    class DataModel(BaseModel):
        reason: str


class AccessDenied(jsonrpc.BaseError):
    CODE = 5005
    MESSAGE = "Access denied"


class NonExistentUser(jsonrpc.BaseError):
    CODE = 5006
    MESSAGE = "User does not exist"
