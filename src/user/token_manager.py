import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Union, Dict, Sequence, Tuple
from fastapi import Response
import jwt

from src.user.auth_config import AuthConfig


class TokenManager(AuthConfig):

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
        return self._create_token(
            subject=subject,
            type_token="access",
            exp_time=self._get_expired_time("access", expires_time),
            fresh=fresh,
            algorithm=algorithm or self._algorithm,
            headers=headers,
            audience=audience,
            user_claims=user_claims,
            issuer=self._encode_issuer
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
        return self._create_token(
            subject=subject,
            type_token="refresh",
            exp_time=self._get_expired_time("refresh", expires_time),
            algorithm=algorithm or self._algorithm,
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
        response.set_cookie(
            self._access_cookie_key,
            encoded_access_token,
            max_age=max_age or self._cookie_max_age,
            path=self._access_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=True,
            samesite=self._cookie_samesite
        )
        response.set_cookie(
            self._access_csrf_cookie_key,
            csrf_token,
            max_age=max_age or self._cookie_max_age,
            path=self._access_csrf_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=False,
            samesite=self._cookie_samesite
        )

    def set_refresh_cookies(
            self,
            encoded_refresh_token: str,
            csrf_token: str,
            response: Optional[Response] = None,
            max_age: Optional[int] = None
    ) -> None:
        response.set_cookie(
            self._refresh_cookie_key,
            encoded_refresh_token,
            max_age=max_age or self._cookie_max_age,
            path=self._refresh_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=True,
            samesite=self._cookie_samesite
        )
        response.set_cookie(
            self._refresh_csrf_cookie_key,
            csrf_token,
            max_age=max_age or self._cookie_max_age,
            path=self._refresh_csrf_cookie_path,
            domain=self._cookie_domain,
            secure=self._cookie_secure,
            httponly=False,
            samesite=self._cookie_samesite
        )

    def unset_jwt_cookies(self,
                          response: Optional[Response] = None
                          ) -> None:
        self.unset_access_cookies(response)
        self.unset_refresh_cookies(response)

    def unset_access_cookies(self,
                             response: Optional[Response] = None
                             ) -> None:
        response.delete_cookie(
            self._access_cookie_key,
            path=self._access_cookie_path,
            domain=self._cookie_domain
        )
        response.delete_cookie(
            self._access_csrf_cookie_key,
            path=self._access_csrf_cookie_path,
            domain=self._cookie_domain
        )

    def unset_refresh_cookies(self,
                              response: Optional[Response] = None
                              ) -> None:
        response.delete_cookie(
            self._refresh_cookie_key,
            path=self._refresh_cookie_path,
            domain=self._cookie_domain
        )
        response.delete_cookie(
            self._refresh_csrf_cookie_key,
            path=self._refresh_csrf_cookie_path,
            domain=self._cookie_domain
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
        custom_claims['csrf'] = self._get_jwt_identifier()
        if exp_time:
            reserved_claims['exp'] = exp_time
        if issuer:
            reserved_claims['iss'] = issuer
        if audience:
            reserved_claims['aud'] = audience
        return jwt.encode(
            {**reserved_claims, **custom_claims, **user_claims},
            self._secret_key,
            algorithm=algorithm or self._algorithm,
            headers=headers
        ), custom_claims['csrf']

    def _get_expired_time(
            self,
            type_token: str,
            expires_time: Optional[Union[timedelta, int, bool]] = None
    ) -> Optional[int]:
        if expires_time is not False:
            if type_token == 'access':
                expires_time = expires_time or self._access_token_expires
            if type_token == 'refresh':
                expires_time = expires_time or self._refresh_token_expires

        if expires_time is not False:
            if isinstance(expires_time, bool):
                if type_token == 'access':
                    expires_time = self._access_token_expires
                if type_token == 'refresh':
                    expires_time = self._refresh_token_expires
            if isinstance(expires_time, timedelta):
                expires_time = int(expires_time.total_seconds())

            return self._get_int_from_datetime(datetime.now(timezone.utc)) + expires_time
        else:
            return None

    def _get_int_from_datetime(self,
                               value: datetime
                               ) -> int:
        return int(value.timestamp())

    def _get_jwt_identifier(self) -> str:
        return str(uuid.uuid4())
