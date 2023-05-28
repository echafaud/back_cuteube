import hmac

from fastapi.security import APIKeyCookie, APIKeyHeader
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError, AccessTokenRequired, RefreshTokenRequired, \
    FreshTokenRequired, CSRFError, JWTDecodeError
from fastapi_users import models
from fastapi import Response, Request, Depends
from fastapi_users.manager import UserManagerDependency, BaseUserManager
from typing import Optional, Union, Dict, List, cast, Callable
from inspect import Signature, Parameter
from fastapi import WebSocket
from makefun import with_signature

from src.auth.exceptions import InvalidAuthenticate
from src.auth.models import User


class Authenticator(AuthJWT):
    def __init__(self, get_user_manager: UserManagerDependency[models.UP, models.ID] = None, req: Request = None,
                 res: Response = None):
        super().__init__(req=req, res=res)
        self.get_user_manager = get_user_manager

    def _verify_and_get_jwt_in_cookies(
            self,
            type_token: str,
            request: Union[Request, WebSocket],
            csrf_token: Optional[str] = None,
            fresh: Optional[bool] = False,
    ) -> "AuthJWT":
        """
        Check if cookies have a valid access or refresh token. if an token present in
        cookies, self._token will set. raises exception error when an access or refresh token
        is invalid or doesn't match with CSRF token double submit

        :param type_token: indicate token is access or refresh token
        :param request: for identity get cookies from HTTP or WebSocket
        :param csrf_token: the CSRF double submit token
        :param fresh: check freshness token if True
        """
        if type_token not in ['access', 'refresh']:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if not isinstance(request, (Request, WebSocket)):
            raise TypeError("request must be an instance of 'Request' or 'WebSocket'")

        if type_token == 'access':
            cookie_key = self._access_cookie_key
            cookie = request.cookies.get(cookie_key)
            if not isinstance(request, WebSocket):
                csrf_token = request.headers.get(self._access_csrf_header_name)
        if type_token == 'refresh':
            cookie_key = self._refresh_cookie_key
            cookie = request.cookies.get(cookie_key)
            if not isinstance(request, WebSocket):
                csrf_token = request.headers.get(self._refresh_csrf_header_name)

        if not cookie:
            pass

        if self._cookie_csrf_protect and not csrf_token:
            if isinstance(request, WebSocket) or request.method in self._csrf_methods:
                raise CSRFError(status_code=200, message="Missing CSRF Token")

        # set token from cookie and verify jwt
        self._token = cookie
        self._verify_jwt_in_request(self._token, type_token, 'cookies', fresh)

        decoded_token = self.get_raw_jwt()

        if self._cookie_csrf_protect and csrf_token:
            if isinstance(request, WebSocket) or request.method in self._csrf_methods:
                if 'csrf' not in decoded_token:
                    raise JWTDecodeError(status_code=200, message="Missing claim: csrf")
                if not hmac.compare_digest(csrf_token, decoded_token['csrf']):
                    raise CSRFError(status_code=200, message="CSRF double submit tokens do not match")

    def current_user(self,
                     token_type: str = None,
                     optional: bool = False,
                     active: bool = False,
                     verified: bool = False,
                     superuser: bool = False, ):

        jwt_token_cookie_name = self._access_cookie_key if token_type == "access" else self._refresh_cookie_key
        csrf_token_header_name = "X-CSRF-Token"
        signature = self._get_dependency_signature(jwt_token_cookie_name, csrf_token_header_name)

        @with_signature(signature)
        async def current_user_dependency(*args, **kwargs):
            user = await self.authenticate(
                *args,
                token_type=token_type,
                jwt_token_name=jwt_token_cookie_name,
                csrf_token_name=csrf_token_header_name.replace('-', '_'),
                optional=optional,
                active=active,
                verified=verified,
                superuser=superuser,
                **kwargs,
            )
            return user

        return current_user_dependency

    async def authenticate(self,
                           *args,
                           user_manager: BaseUserManager[models.UP, models.ID],
                           token_type: str,
                           jwt_token_name: str,
                           csrf_token_name: str,
                           optional: bool = False,
                           active: bool = False,
                           verified: bool = False,
                           superuser: bool = False,
                           **kwargs) -> Optional[models.UP]:
        token, csrf = kwargs[jwt_token_name], kwargs[csrf_token_name]
        if token is not None and csrf is not None:
            user = await self.read_token(token=token, token_type=token_type, user_manager=user_manager, csrf_token=csrf)
            if active and not user.is_active:
                raise InvalidAuthenticate(data={'reason': 'Current user is not authorized'})
            elif verified and not user.is_verified:
                raise InvalidAuthenticate(data={'reason': 'Current user is not verified'})
            elif superuser and not user.is_superuser:
                raise InvalidAuthenticate(data={'reason': 'Not enough rights'})
        elif optional:
            return User()
        else:
            raise InvalidAuthenticate(data={'reason': f'Missing {token_type} token or {csrf_token_name} Token'})
        return user

    def _get_dependency_signature(
            self, jwt_token_cookie_name: str, csrf_token_header_name: str
    ) -> Signature:
        """
        Generate a dynamic signature for the current_user dependency.

        Here comes some blood magic 🧙‍♂️
        Thank to "makefun", we are able to generate callable
        with a dynamic number of dependencies at runtime.
        This way, each security schemes are detected by the OpenAPI generator.
        """
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

    async def read_token(self,
                         token_type: str,
                         auth_from: str = "request",
                         token: Optional[str] = None,
                         websocket: Optional[WebSocket] = None,
                         csrf_token: Optional[str] = None,
                         user_manager: BaseUserManager[models.UP, models.ID] = None,
                         ):
        if auth_from == "websocket":
            if websocket:
                self._verify_and_get_jwt_in_cookies(token_type, websocket, csrf_token)
            else:
                self._verify_jwt_in_request(token, token_type, 'websocket')

        if auth_from == "request":
            token = await self.adv_verify_and_get_jwt_in_cookies(token_type=token_type, token=token,
                                                                 csrf_token=csrf_token)
            user_id = token['sub']
            return await user_manager.get(user_id)
        return None

    async def adv_verify_and_get_jwt_in_cookies(self,
                                                token_type: str,
                                                token: Union[str, WebSocket],
                                                csrf_token: Optional[str] = None,
                                                fresh: Optional[bool] = False, ):
        if token_type not in ['access', 'refresh']:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        # if not isinstance(request, (Request, WebSocket)):
        #     raise TypeError("request must be an instance of 'Request' or 'WebSocket'")

        # if type_token == 'access':
        #     cookie_key = self._access_cookie_key
        #     cookie = request.cookies.get(cookie_key)
        #     if not isinstance(request, WebSocket):
        #         csrf_token = request.headers.get(self._access_csrf_header_name)
        # if type_token == 'refresh':
        #     cookie_key = self._refresh_cookie_key
        #     cookie = request.cookies.get(cookie_key)
        #     if not isinstance(request, WebSocket):
        #         csrf_token = request.headers.get(self._refresh_csrf_header_name)

        if not token:
            raise InvalidAuthenticate(data={'reason': f'{token_type} token not found'})

        # if self._cookie_csrf_protect and not csrf_token:
        #     if isinstance(request, WebSocket) or request.method in self._csrf_methods:
        #         raise CSRFError(status_code=200, message="Missing CSRF Token")

        # set token from cookie and verify jwt
        decoded_token = await self.adv_verify_jwt_in_request(token, token_type, 'cookies', fresh)
        if self._cookie_csrf_protect and csrf_token:
            # if isinstance(request, WebSocket) or request.method in self._csrf_methods:
            if 'csrf' not in decoded_token:
                raise InvalidAuthenticate(data={'reason': 'Missing csrf token in jwt'})
            if not hmac.compare_digest(csrf_token, decoded_token['csrf']):
                raise InvalidAuthenticate(data={'reason': 'CSRF double submit tokens do not match'})
        return decoded_token

    async def adv_verify_jwt_in_request(
            self,
            token: str,
            token_type: str,
            token_from: str,
            fresh: Optional[bool] = False
    ) -> Dict[str, Union[str, int, bool]]:
        """
        Ensure that the requester has a valid token. this also check the freshness of the access token

        :param token: The encoded JWT
        :param token_type: indicate token is access or refresh token
        :param token_from: indicate token from headers cookies, websocket
        :param fresh: check freshness token if True
        """
        if token_type not in ['access', 'refresh']:
            raise ValueError("type_token must be between 'access' or 'refresh'")
        if token_from not in ['headers', 'cookies', 'websocket']:
            raise ValueError("token_from must be between 'headers', 'cookies', 'websocket'")
        #
        # if not token:
        #     if token_from == 'headers':
        #         raise MissingTokenError(status_code=401, message="Missing {} Header".format(self._header_name))
        #     if token_from == 'websocket':
        #         raise MissingTokenError(status_code=1008,
        #                                 message="Missing {} token from Query or Path".format(token_type))

        # verify jwt
        issuer = self._decode_issuer if token_type == 'access' else None
        decoded_token = self.adv_verifying_token(token, issuer)

        if decoded_token['type'] != token_type:
            raise InvalidAuthenticate(data={'reason': f'Only {token_type} tokens are allowed'})
            # msg = "Only {} tokens are allowed".format(token_type)
            # if token_type == 'access':
            #     raise InvalidAuthenticate(data={'reason': f'Only {token_type} tokens are allowed'})
            # if token_type == 'refresh':
            #     raise RefreshTokenRequired(status_code=422, message=msg)

        if fresh and not decoded_token['fresh']:
            raise FreshTokenRequired(status_code=401, message="Fresh token required")
        return decoded_token

    def adv_verifying_token(self, encoded_token: str, issuer: Optional[str] = None) -> Dict[str, Union[str, int, bool]]:
        """
        Verified token and check if token is revoked

        :param encoded_token: token hash
        :param issuer: expected issuer in the JWT
        """
        raw_token = self._verified_token(encoded_token, issuer)
        if raw_token['type'] in self._denylist_token_checks:
            self._check_token_is_revoked(raw_token)

        return raw_token
