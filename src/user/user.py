from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_db_session
from src.redis_manager.redis import get_redis_manager
from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth_user_manager import AuthUserManager
from src.user.models import User
from src.user.user_database_adapter import UserDatabaseAdapter
from src.user.user_manager import UserManager


async def get_user_db(session: AsyncSession = Depends(get_async_db_session)):
    yield UserDatabaseAdapter(session, User)


async def get_auth_user_manager(user_db=Depends(get_user_db), redis_manager=Depends(get_redis_manager)):
    yield AuthUserManager(user_db, redis_manager=redis_manager)


async def get_user_manager(auth_manager=Depends(get_auth_user_manager),
                           subscription_manager: SubscriptionManager = Depends(get_subscription_manager)):
    yield UserManager(auth_manager, subscription_manager)
