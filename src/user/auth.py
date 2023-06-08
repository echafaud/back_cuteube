from fastapi import Depends
from pydantic import BaseModel
from src.user.authentication_backend import AdvancedAuthenticationBackend
from src.user.authenticator import Authenticator
from src.user.token_manager import TokenManager
from src.user.auth_user_manager import AuthUserManager
from src.config import SECRET
from src.user.user import get_auth_user_manager, get_user_manager


class Settings(BaseModel):
    secret_key: str = SECRET
    # Configure application to store and get JWT from cookies
    token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    cookie_csrf_protect: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    # authjwt_cookie_samesite: str = 'lax'


@Authenticator.load_config
def get_config():
    return Settings()


@TokenManager.load_config
def get_config():
    return Settings()


token_manager = TokenManager()
advanced_authentication_backend = AdvancedAuthenticationBackend(token_manager)

adv_auth = Authenticator(get_user_manager)

access_user = adv_auth.authenticate_current_user(token_type="access")

refresh_user = adv_auth.authenticate_current_user(token_type="refresh")
optional_access_user = adv_auth.authenticate_current_user(token_type="access", optional=True)
