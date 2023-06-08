import hmac
import jwt
import fastapi_jsonrpc as jsonrpc
from fastapi.security import APIKeyCookie, APIKeyHeader
from fastapi import Depends
from typing import Optional, Union, Dict, List, cast, Callable
from inspect import Signature, Parameter
from fastapi import WebSocket
from makefun import with_signature

from src.user.auth_config import AuthConfig
from src.user.exceptions import InvalidAuthenticate, AccessDenied
from src.user.models import User
from src.user.user_manager import UserManager


class Authenticator(AuthConfig):
    def __init__(
            self,
            get_user_manager: Callable = None):
        self.get_user_manager = get_user_manager

    def authenticate_current_user(self,
                                  token_type: str = None,
                                  optional: bool = False,
                                  active: bool = False,
                                  verified: bool = False,
                                  superuser: bool = False,
                                  ) -> Callable:

        jwt_token_cookie_name = self._access_cookie_key if token_type == "access" else self._refresh_cookie_key
        csrf_header_name = self._access_csrf_header_name if token_type == "access" else self._refresh_csrf_header_name
        signature = self._get_dependency_signature(jwt_token_cookie_name, csrf_header_name)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            try:
                user = await self.authenticate(
                    *args,
                    token_type=token_type,
                    jwt_token_name=jwt_token_cookie_name,
                    csrf_token_name=self._access_csrf_header_name.replace('-', '_'),
                    optional=optional,
                    active=active,
                    verified=verified,
                    superuser=superuser,
                    **kwargs,
                )
            except InvalidAuthenticate:
                raise AccessDenied
            return user

        return current_user_dependency

    async def authenticate(self,
                           *args,
                           user_manager: UserManager,
                           token_type: str,
                           jwt_token_name: str,
                           csrf_token_name: str,
                           optional: bool = False,
                           active: bool = False,
                           verified: bool = False,
                           superuser: bool = False,
                           **kwargs
                           ) -> Optional[User]:
        token, csrf = kwargs[jwt_token_name], kwargs[csrf_token_name]
        if token is not None and csrf is not None:
            user = await self.read_token(token_type, token, csrf, user_manager)
            if active and not user.is_active:
                raise InvalidAuthenticate(data={'reason': 'Current user is not authorized'})
            elif verified and not user.is_verified:
                raise InvalidAuthenticate(data={'reason': 'Current user is not verified'})
            elif superuser and not user.is_superuser:
                raise InvalidAuthenticate(data={'reason': 'Not enough rights'})
        elif optional:
            return User()
        else:
            raise InvalidAuthenticate(data={'reason': f'Missing {token_type} token or {csrf_token_name} token'})
        return user

    async def read_token(self,
                         token_type: str,
                         token: Optional[str] = None,
                         csrf_token: Optional[str] = None,
                         user_manager: UserManager = None,
                         ):
        token = await self.get_token(token_type, token, csrf_token)
        user_id = token['sub']
        return await user_manager.get(user_id)

    async def get_token(self,
                        token_type: str,
                        token: Union[str, WebSocket],
                        csrf_token: Optional[str] = None,
                        fresh: Optional[bool] = False, ):
        decoded_token = await self.get_decoded_token(token_type, token, fresh)
        if self._cookie_csrf_protect and csrf_token:
            if 'csrf' not in decoded_token:
                raise InvalidAuthenticate(data={'reason': 'Missing csrf token in jwt'})
            if not hmac.compare_digest(csrf_token, decoded_token['csrf']):
                raise InvalidAuthenticate(data={'reason': 'CSRF double submit tokens do not match'})
        return decoded_token

    async def get_decoded_token(
            self,
            token_type: str,
            token: str,
            fresh: Optional[bool] = False
    ) -> Dict[str, Union[str, int, bool]]:
        issuer = self._decode_issuer if token_type == 'access' else None
        decoded_token = self.verify_token(token, issuer)

        if decoded_token['type'] != token_type:
            raise InvalidAuthenticate(data={'reason': f'Only {token_type} tokens are allowed'})

        if fresh and not decoded_token['fresh']:
            raise InvalidAuthenticate(data={'reason': f'Fresh token required'})
        return decoded_token

    def verify_token(
            self,
            encoded_token: str,
            issuer: Optional[str] = None
    ) -> Dict[str, Union[str, int, bool]]:
        decoded_token = self._verify_token(encoded_token, issuer)
        if decoded_token['type'] in self._denylist_token_checks:
            self._check_token_is_revoked(decoded_token)

        return decoded_token

    def get_unverified_headers(
            self,
            encoded_token: str
    ) -> dict:
        return jwt.get_unverified_header(encoded_token)

    def _verify_token(
            self,
            encoded_token: str,
            issuer: Optional[str] = None
    ) -> Dict[str, Union[str, int, bool]]:
        algorithms = self._decode_algorithms or [self._algorithm]

        try:
            self.get_unverified_headers(encoded_token)
        except Exception as err:
            raise InvalidAuthenticate(data={'reason': str(err)})
        try:
            return jwt.decode(
                encoded_token,
                self._secret_key,
                issuer=issuer,
                audience=self._decode_audience,
                leeway=self._decode_leeway,
                algorithms=algorithms
            )
        except Exception as err:
            raise InvalidAuthenticate(data={'reason': str(err)})

    def _get_dependency_signature(
            self,
            jwt_token_cookie_name: str,
            csrf_token_header_name: str
    ) -> Signature:
        parameters: List[Parameter] = [
            Parameter(
                name="user_manager",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(self.get_user_manager),
            ),
            Parameter(
                name=jwt_token_cookie_name,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, APIKeyCookie(name=jwt_token_cookie_name, auto_error=False))),
            ),
            Parameter(
                name=csrf_token_header_name.replace('-', '_'),
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                default=Depends(cast(Callable, APIKeyHeader(name=csrf_token_header_name, auto_error=False))),
            ),
        ]

        return Signature(parameters)

    def _check_token_is_revoked(
            self,
            raw_token: Dict[str, Union[str, int, bool]]
    ) -> None:
        if not self._denylist_enabled:
            return

        if self._token_in_denylist_callback.__func__(raw_token):
            raise InvalidAuthenticate(data={'reason': 'Token has been revoked'})
