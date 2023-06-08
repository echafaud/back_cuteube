from datetime import timedelta
from typing import Optional, Union, Sequence, List
from pydantic import (
    BaseModel,
    validator,
    StrictBool,
    StrictInt,
    StrictStr
)


class LoadConfig(BaseModel):
    secret_key: Optional[StrictStr] = None
    public_key: Optional[StrictStr] = None
    private_key: Optional[StrictStr] = None
    algorithm: Optional[StrictStr] = "HS256"
    decode_algorithms: Optional[List[StrictStr]] = None
    decode_leeway: Optional[Union[StrictInt, timedelta]] = 0
    encode_issuer: Optional[StrictStr] = None
    decode_issuer: Optional[StrictStr] = None
    decode_audience: Optional[Union[StrictStr, Sequence[StrictStr]]] = None
    denylist_enabled: Optional[StrictBool] = False
    denylist_token_checks: Optional[Sequence[StrictStr]] = {'access', 'refresh'}
    access_token_expires: Optional[Union[StrictBool, StrictInt, timedelta]] = timedelta(minutes=15)
    refresh_token_expires: Optional[Union[StrictBool, StrictInt, timedelta]] = timedelta(days=30)

    access_cookie_key: Optional[StrictStr] = "access_token_cookie"
    refresh_cookie_key: Optional[StrictStr] = "refresh_token_cookie"
    access_cookie_path: Optional[StrictStr] = "/"
    refresh_cookie_path: Optional[StrictStr] = "/"
    cookie_max_age: Optional[StrictInt] = None
    cookie_domain: Optional[StrictStr] = None
    cookie_secure: Optional[StrictBool] = False
    cookie_samesite: Optional[StrictStr] = None

    cookie_csrf_protect: Optional[StrictBool] = True
    access_csrf_cookie_key: Optional[StrictStr] = "csrf_access_token"
    refresh_csrf_cookie_key: Optional[StrictStr] = "csrf_refresh_token"
    access_csrf_cookie_path: Optional[StrictStr] = "/"
    refresh_csrf_cookie_path: Optional[StrictStr] = "/"
    access_csrf_header_name: Optional[StrictStr] = "X-CSRF-Token"
    refresh_csrf_header_name: Optional[StrictStr] = "X-CSRF-Token"
    csrf_methods: Optional[Sequence[StrictStr]] = {'POST', 'PUT', 'PATCH', 'DELETE'}
