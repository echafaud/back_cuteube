from pydantic import ValidationError
from typing import Callable, List
from datetime import timedelta

from src.user.auth_load_config import LoadConfig


class AuthConfig:
    _secret_key = None
    _public_key = None
    _private_key = None
    _algorithm = "HS256"
    _decode_algorithms = None
    _decode_leeway = 0
    _encode_issuer = None
    _decode_issuer = None
    _decode_audience = None
    _denylist_enabled = False
    _denylist_token_checks = {'access', 'refresh'}
    _token_in_denylist_callback = None
    _access_token_expires = timedelta(minutes=15)
    _refresh_token_expires = timedelta(days=30)

    _access_cookie_key = "access_token_cookie"
    _refresh_cookie_key = "refresh_token_cookie"
    _access_cookie_path = "/"
    _refresh_cookie_path = "/"
    _cookie_max_age = None
    _cookie_domain = None
    _cookie_secure = False
    _cookie_samesite = None

    _cookie_csrf_protect = True
    _access_csrf_cookie_key = "csrf_access_token"
    _refresh_csrf_cookie_key = "csrf_refresh_token"
    _access_csrf_cookie_path = "/"
    _refresh_csrf_cookie_path = "/"
    _access_csrf_header_name = "X-CSRF-Token"
    _refresh_csrf_header_name = "X-CSRF-Token"
    _csrf_methods = {'POST'}

    @classmethod
    def load_config(cls, settings: Callable[..., List[tuple]]):
        try:
            config = LoadConfig(**{key.lower(): value for key, value in settings()})
            cls._secret_key = config.secret_key
            cls._public_key = config.public_key
            cls._private_key = config.private_key
            cls._algorithm = config.algorithm
            cls._decode_algorithms = config.decode_algorithms
            cls._decode_leeway = config.decode_leeway
            cls._encode_issuer = config.encode_issuer
            cls._decode_issuer = config.decode_issuer
            cls._decode_audience = config.decode_audience
            cls._denylist_enabled = config.denylist_enabled
            cls._denylist_token_checks = config.denylist_token_checks
            cls._access_token_expires = config.access_token_expires
            cls._refresh_token_expires = config.refresh_token_expires

            cls._access_cookie_key = config.access_cookie_key
            cls._refresh_cookie_key = config.refresh_cookie_key
            cls._access_cookie_path = config.access_cookie_path
            cls._refresh_cookie_path = config.refresh_cookie_path
            cls._cookie_max_age = config.cookie_max_age
            cls._cookie_domain = config.cookie_domain
            cls._cookie_secure = config.cookie_secure
            cls._cookie_samesite = config.cookie_samesite

            cls._cookie_csrf_protect = config.cookie_csrf_protect
            cls._access_csrf_cookie_key = config.access_csrf_cookie_key
            cls._refresh_csrf_cookie_key = config.refresh_csrf_cookie_key
            cls._access_csrf_cookie_path = config.access_csrf_cookie_path
            cls._refresh_csrf_cookie_path = config.refresh_csrf_cookie_path
            cls._access_csrf_header_name = config.access_csrf_header_name
            cls._refresh_csrf_header_name = config.refresh_csrf_header_name
            cls._csrf_methods = config.csrf_methods
        except ValidationError:
            raise
        except Exception:
            raise TypeError("Config must be pydantic 'BaseSettings' or list of tuple")

    @classmethod
    def token_in_denylist_loader(cls, callback: Callable[..., bool]):
        """
        This decorator sets the callback function that will be called when
        a protected endpoint is accessed and will check if the JWT has been
        been revoked. By default, this callback is not used.

        *HINT*: The callback must be a function that takes decrypted_token argument,
        args for object AuthJWT and this is not used, decrypted_token is decode
        JWT (python dictionary) and returns *`True`* if the token has been deny,
        or *`False`* otherwise.
        """
        cls._token_in_denylist_callback = callback
