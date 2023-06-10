import fastapi_jsonrpc as jsonrpc


class NonExistentLike(jsonrpc.BaseError):
    CODE = 7000
    MESSAGE = "Like does not exist"


class SameStatusException(jsonrpc.BaseError):
    CODE = 7001
    MESSAGE = "Current rating matches the established one"
