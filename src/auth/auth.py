from fastapi import Depends
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.authentication_backend import AdvancedAuthenticationBackend
from src.auth.models import User
from src.auth.token_manager import TokenManager
from src.auth.user_database_adapter import UserDatabaseAdapter
from src.auth.user_manager import UserManager
from src.config import SECRET
from src.database import get_async_session


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


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield UserDatabaseAdapter(session, User)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
