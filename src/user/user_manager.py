from typing import Optional
from uuid import UUID

from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth_user_manager import AuthUserManager
from src.user.exceptions import NonExistentUser
from src.user.models import User
from src.user.shemas import UserCreate, UserLogin, UserRead


class UserManager:
    def __init__(self, auth_manager: AuthUserManager, subscription_manager: SubscriptionManager):
        self.user_db = auth_manager.user_db
        self.auth_manager = auth_manager
        self.subscription_manager = subscription_manager

    async def get(self,
                  user_id: UUID,
                  ) -> Optional[User]:
        return await self.user_db.get(user_id)

    async def get_user_read(self,
                            user_id: UUID,
                            current_user: Optional[User] = None
                            ) -> Optional[UserRead]:
        requested_user = await self.user_db.get(user_id)
        if not requested_user:
            raise NonExistentUser
        user_read = UserRead.from_orm(requested_user)
        user_read.count_subscribers = await self.subscription_manager.count_user_subscribers(requested_user)
        if current_user and current_user.id:
            subscription = await self.subscription_manager.get_user_subscribed(current_user, requested_user)
            user_read.is_subscribed = True if subscription else False
        else:
            user_read.is_subscribed = None
        return user_read

    async def create(self,
                     user_create: UserCreate,
                     ) -> User:
        return await self.auth_manager.create(user_create, True)

    async def authenticate(self,
                           credentials: UserLogin
                           ) -> User:
        return await self.auth_manager.authenticate(credentials)

    async def on_after_login(self,
                             user: User
                             ) -> None:
        await self.auth_manager.on_after_login(user)

    async def on_after_logout(self,
                              user: User
                              ) -> None:
        await self.auth_manager.on_after_logout(user)
