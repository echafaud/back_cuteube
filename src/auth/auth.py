from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from pydantic import BaseModel

from src.auth.authentication_backend import AdvancedAuthenticationBackend
from src.auth.token_manager import TokenManager
from src.config import SECRET


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_secure: bool = False
    # Enable csrf double submit protection. default is True
    authjwt_cookie_csrf_protect: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None
    # authjwt_cookie_samesite: str = 'lax'


token_manager = TokenManager(SECRET)
advanced_authentication_backend = AdvancedAuthenticationBackend(
    # name="jwt",
    # transport=cookie_transport,
    # get_strategy=get_jwt_strategy,
    token_manager=token_manager)
