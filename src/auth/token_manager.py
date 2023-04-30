import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Dict, Sequence, Tuple
from fastapi import Response
import jwt


class TokenManager:
    def __init__(self, secret_key: str,
                 access_cookie_key: str = "access_token_cookie",
                 access_cookie_path: str = "/",
                 access_csrf_cookie_key: str = "csrf_access_token",
                 access_csrf_cookie_path: str = "/",
                 access_token_expires: timedelta = timedelta(minutes=15),
                 refresh_cookie_key: str = "refresh_token_cookie",
                 refresh_cookie_path: str = "/",
                 refresh_csrf_cookie_key: str = "csrf_refresh_token",
                 refresh_csrf_cookie_path: str = "/",
                 refresh_token_expires: timedelta = timedelta(days=30),
                 algorithm: str = "HS256",
                 cookie_max_age: Optional[int] = None,
                 cookie_domain: Optional[str] = None,
                 cookie_secure: bool = False,
                 cookie_samesite: Optional[str] = None,
                 encode_issuer: str = None,

                 ):
        self.secret_key = secret_key
        self.access_cookie_key = access_cookie_key
        self.access_cookie_path = access_cookie_path
        self.access_csrf_cookie_key = access_csrf_cookie_key
        self.access_csrf_cookie_path = access_csrf_cookie_path
        self.access_token_expires = access_token_expires
        self.refresh_cookie_key = refresh_cookie_key
        self.refresh_cookie_path = refresh_cookie_path
        self.refresh_csrf_cookie_key = refresh_csrf_cookie_key
        self.refresh_csrf_cookie_path = refresh_csrf_cookie_path
        self.refresh_token_expires = refresh_token_expires
        self.algorithm = algorithm
        self.cookie_max_age = cookie_max_age
        self.encode_issuer = encode_issuer
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_samesite = cookie_samesite

    def create_access_tokens(
            self,
            subject: Union[str, int],
            fresh: Optional[bool] = False,
            algorithm: Optional[str] = None,
            headers: Optional[Dict] = None,
            expires_time: Optional[Union[timedelta, int, bool]] = None,
            audience: Optional[Union[str, Sequence[str]]] = None,
            user_claims: Optional[Dict] = {}
    ) -> Tuple[str, str]:
        """
        Create a access token with 15 minutes for expired time (default),
        info for param and return check to function create token

        :return: hash token
        """
        return self._create_token(
            subject=subject,
            type_token="access",
            exp_time=self._get_expired_time("access", expires_time),
            fresh=fresh,
            algorithm=algorithm or self.algorithm,
            headers=headers,
            audience=audience,
            user_claims=user_claims,
            issuer=self.encode_issuer
        )

    def create_refresh_tokens(
            self,
            subject: Union[str, int],
            algorithm: Optional[str] = None,
            headers: Optional[Dict] = None,
            expires_time: Optional[Union[timedelta, int, bool]] = None,
            audience: Optional[Union[str, Sequence[str]]] = None,
            user_claims: Optional[Dict] = {}
    ) -> Tuple[str, str]:
        """
        Create a refresh token with 30 days for expired time (default),
        info for param and return check to function create token

        :return: hash token
        """
        return self._create_token(
            subject=subject,
            type_token="refresh",
            exp_time=self._get_expired_time("refresh", expires_time),
            algorithm=algorithm or self.algorithm,
            headers=headers,
            audience=audience,
            user_claims=user_claims
        )

    def set_access_cookies(
            self,
            encoded_access_token: str,
            csrf_token: str,
            response: Optional[Response] = None,
            max_age: Optional[int] = None
    ) -> None:
        """
        Configures the response to set access token in a cookie.
        this will also set the CSRF double submit values in a separate cookie

        :param csrf_token:
        :param encoded_access_token: The encoded access token to set in the cookies
        :param response: The FastAPI response object to set the access cookies in
        :param max_age: The max age of the cookie value should be the number of seconds (integer)
        """

        if max_age and not isinstance(max_age, int):
            raise TypeError("max_age must be a integer")
        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        # Set the access JWT in the cookie
        response.set_cookie(
            self.access_cookie_key,
            encoded_access_token,
            max_age=max_age or self.cookie_max_age,
            path=self.access_cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=True,
            samesite=self.cookie_samesite
        )
        # If enabled, set the csrf double submit access cookie
        response.set_cookie(
            self.access_csrf_cookie_key,
            csrf_token,
            max_age=max_age or self.cookie_max_age,
            path=self.access_csrf_cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=False,
            samesite=self.cookie_samesite
        )

    def set_refresh_cookies(
            self,
            encoded_refresh_token: str,
            csrf_token: str,
            response: Optional[Response] = None,
            max_age: Optional[int] = None
    ) -> None:
        """
        Configures the response to set refresh token in a cookie.
        this will also set the CSRF double submit values in a separate cookie

        :param csrf_token:
        :param encoded_refresh_token: The encoded refresh token to set in the cookies
        :param response: The FastAPI response object to set the refresh cookies in
        :param max_age: The max age of the cookie value should be the number of seconds (integer)
        """

        if max_age and not isinstance(max_age, int):
            raise TypeError("max_age must be a integer")
        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        # Set the refresh JWT in the cookie
        response.set_cookie(
            self.refresh_cookie_key,
            encoded_refresh_token,
            max_age=max_age or self.cookie_max_age,
            path=self.refresh_cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=True,
            samesite=self.cookie_samesite
        )

        # If enabled, set the csrf double submit refresh cookie
        response.set_cookie(
            self.refresh_csrf_cookie_key,
            csrf_token,
            max_age=max_age or self.cookie_max_age,
            path=self.refresh_csrf_cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=False,
            samesite=self.cookie_samesite
        )

    def unset_jwt_cookies(self, response: Optional[Response] = None) -> None:
        """
        Unset (delete) all jwt stored in a cookie

        :param response: The FastAPI response object to delete the JWT cookies in.
        """
        self.unset_access_cookies(response)
        self.unset_refresh_cookies(response)

    def unset_access_cookies(self, response: Optional[Response] = None) -> None:
        """
        Remove access token and access CSRF double submit from the response cookies

        :param response: The FastAPI response object to delete the access cookies in.
        """

        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response.delete_cookie(
            self.access_cookie_key,
            path=self.access_cookie_path,
            domain=self.cookie_domain
        )

        response.delete_cookie(
            self.access_csrf_cookie_key,
            path=self.access_csrf_cookie_path,
            domain=self.cookie_domain
        )

    def unset_refresh_cookies(self, response: Optional[Response] = None) -> None:
        """
        Remove refresh token and refresh CSRF double submit from the response cookies

        :param response: The FastAPI response object to delete the refresh cookies in.
        """

        if response and not isinstance(response, Response):
            raise TypeError("The response must be an object response FastAPI")

        response.delete_cookie(
            self.refresh_cookie_key,
            path=self.refresh_cookie_path,
            domain=self.cookie_domain
        )

        response.delete_cookie(
            self.refresh_csrf_cookie_key,
            path=self.refresh_csrf_cookie_path,
            domain=self.cookie_domain
        )

    def _create_token(
            self,
            subject: Union[str, int],
            type_token: str,
            exp_time: Optional[int],
            fresh: Optional[bool] = False,
            algorithm: Optional[str] = None,
            headers: Optional[Dict] = None,
            issuer: Optional[str] = None,
            audience: Optional[Union[str, Sequence[str]]] = None,
            user_claims: Optional[Dict] = {}
    ) -> Tuple[str, str]:
        """
        Create token for access_token and refresh_token (utf-8)

        :param subject: Identifier for who this token is for example id or username from database.
        :param type_token: indicate token is access_token or refresh_token
        :param exp_time: Set the duration of the JWT
        :param fresh: Optional when token is access_token this param required
        :param algorithm: algorithm allowed to encode the token
        :param headers: valid dict for specifying additional headers in JWT header section
        :param issuer: expected issuer in the JWT
        :param audience: expected audience in the JWT
        :param user_claims: Custom claims to include in this token. This data must be dictionary

        :return: Encoded token
        """
        # Validation type data
        if not isinstance(subject, (str, int, uuid.UUID)):
            raise TypeError("subject must be a string or integer")
        if not isinstance(fresh, bool):
            raise TypeError("fresh must be a boolean")
        if audience and not isinstance(audience, (str, list, tuple, set, frozenset)):
            raise TypeError("audience must be a string or sequence")
        if algorithm and not isinstance(algorithm, str):
            raise TypeError("algorithm must be a string")
        if user_claims and not isinstance(user_claims, dict):
            raise TypeError("user_claims must be a dictionary")

        # Data section
        reserved_claims = {
            "sub": str(subject),
            "iat": self._get_int_from_datetime(datetime.now(timezone.utc)),
            "nbf": self._get_int_from_datetime(datetime.now(timezone.utc)),
            "jti": self._get_jwt_identifier()
        }

        custom_claims = {"type": type_token}

        # for access_token only fresh needed
        if type_token == 'access':
            custom_claims['fresh'] = fresh
        # if cookie in token location and csrf protection enabled
        # if self.jwt_in_cookies and self._cookie_csrf_protect:
        custom_claims['csrf'] = self._get_jwt_identifier()

        if exp_time:
            reserved_claims['exp'] = exp_time
        if issuer:
            reserved_claims['iss'] = issuer
        if audience:
            reserved_claims['aud'] = audience

        return jwt.encode(
            {**reserved_claims, **custom_claims, **user_claims},
            self.secret_key,
            algorithm=algorithm or self.algorithm,
            headers=headers
        ), custom_claims['csrf']

    def _get_expired_time(
            self,
            type_token: str,
            expires_time: Optional[Union[timedelta, int, bool]] = None
    ) -> Union[None, int]:
        """
        Dynamic token expired, if expires_time is False exp claim not created

        :param type_token: indicate token is access_token or refresh_token
        :param expires_time: duration expired jwt

        :return: duration exp claim jwt
        """
        if expires_time and not isinstance(expires_time, (timedelta, int, bool)):
            raise TypeError("expires_time must be between timedelta, int, bool")

        if expires_time is not False:
            if type_token == 'access':
                expires_time = expires_time or self.access_token_expires
            if type_token == 'refresh':
                expires_time = expires_time or self.refresh_token_expires

        if expires_time is not False:
            if isinstance(expires_time, bool):
                if type_token == 'access':
                    expires_time = self.access_token_expires
                if type_token == 'refresh':
                    expires_time = self.refresh_token_expires
            if isinstance(expires_time, timedelta):
                expires_time = int(expires_time.total_seconds())

            return self._get_int_from_datetime(datetime.now(timezone.utc)) + expires_time
        else:
            return None

    def _get_int_from_datetime(self, value: datetime) -> int:
        """
        :param value: datetime with or without timezone, if don't contains timezone
                      it will managed as it is UTC
        :return: Seconds since the Epoch
        """
        if not isinstance(value, datetime):  # pragma: no cover
            raise TypeError('a datetime is required')
        return int(value.timestamp())

    def _get_jwt_identifier(self) -> str:
        return str(uuid.uuid4())
