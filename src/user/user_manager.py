from typing import Optional, List, Any
from uuid import UUID

from src.celery_main import celery
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth_user_manager import AuthUserManager
from src.user.exceptions import NonExistentUser, UserVerifyException
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
        user_read = await self.convert_user_to_user_read(current_user, requested_user)
        return user_read

    async def create(self,
                     user_create: UserCreate,
                     ) -> User:
        return await self.auth_manager.create(user_create, True)

    async def authenticate(self,
                           credentials: UserLogin
                           ) -> User:
        return await self.auth_manager.authenticate(credentials)

    async def verify(self,
                     user_id: UUID,
                     token: UUID
                     ) -> None:
        user = await self.get(user_id)
        if not user:
            raise NonExistentUser
        if user.is_verified:
            raise UserVerifyException(data={'reason': 'User has already been verified'})
        await self.auth_manager.verify(user, token)
        await self.user_db.update(user, {'is_verified': True})

    async def update_verify(self,
                            user_id: UUID
                            ) -> None:
        user = await self.get(user_id)
        if not user:
            raise NonExistentUser
        if user.is_verified:
            raise UserVerifyException(data={'reason': 'User has already been verified'})
        await self.auth_manager.update_verify(user)

    async def on_after_login(self,
                             user: User
                             ) -> None:
        await self.auth_manager.on_after_login(user)

    async def on_after_logout(self,
                              user: User
                              ) -> None:
        await self.auth_manager.on_after_logout(user)

    async def check_existing(self,
                             user_id
                             ) -> bool:
        user = await self.user_db.get(user_id)
        return True if user else False

    async def convert_user_to_user_read(self,
                                        current_user: User,
                                        requested_user: User,
                                        ) -> UserRead:
        user_read = UserRead.from_orm(requested_user)
        user_read.count_subscribers = await self.count_subscribers(requested_user)
        if current_user and current_user.id:
            subscription = await self.subscription_manager.get_user_subscribed(current_user, requested_user)
            user_read.is_subscribed = True if subscription else False
        else:
            user_read.is_subscribed = None
        return user_read

    async def get_subscribed(self,
                             limit: int,
                             pagination: int,
                             user: User):
        subscribed = await self.user_db.get_user_relationship(user.subscribed)
        result = [await self.convert_user_to_user_read(user, subscribed_user) for subscribed_user in subscribed]
        return self._paginate(limit, pagination, result)

    async def get_subscribers(self,
                              user: User):
        return await self.user_db.get_user_relationship(user.subscribers)

    async def count_subscribers(self,
                                user: User):
        return len(await self.get_subscribers(user))

    def _paginate(self,
                  limit,
                  pagination,
                  result) -> List[Any]:
        return result[limit * pagination: limit * (pagination + 1)]
