from fastapi import Response
from fastapi_users import models

from src.auth.exceptions import LoginBadCredentials
from src.auth.token_manager import TokenManager


class AdvancedAuthenticationBackend:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager

    def advanced_login(self, response: Response, user: models.UP):
        if user is None:  # or user.is_active
            raise LoginBadCredentials
        jwt_access_token, csrf_access_token = self.token_manager.create_access_tokens(subject=user.id)
        jwt_refresh_token, csrf_refresh_token = self.token_manager.create_refresh_tokens(subject=user.id)

        self.token_manager.set_access_cookies(jwt_access_token, csrf_access_token, response=response)
        self.token_manager.set_refresh_cookies(jwt_refresh_token, csrf_refresh_token, response=response)

    def refresh(self, response: Response, user: models.UP):
        jwt_access_token, csrf_access_token = self.token_manager.create_access_tokens(subject=user.id)

        self.token_manager.set_access_cookies(jwt_access_token, csrf_access_token, response=response)

    def advanced_logout(self, response: Response, user: models.UP):
        self.token_manager.unset_jwt_cookies(response=response)
