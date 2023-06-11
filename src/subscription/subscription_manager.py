from uuid import UUID

from src.subscription.exceptions import NonExistentSubscription, SubscribeException, UnSubscribeException
from src.user.models import User
from src.subscription.shemas import BaseSubscription
from src.subscription.subscription_database_adapter import SubscriptionDatabaseAdapter


class SubscriptionManager:
    def __init__(self,
                 subscription_db: SubscriptionDatabaseAdapter):
        self.subscription_db = subscription_db

    async def subscribe(self,
                        subscribed_id: UUID,
                        user: User
                        ) -> None:
        if subscribed_id == user.id:
            raise SubscribeException(data={'reason': 'You cant subscribe to yourself'})

        subscription = await self.subscription_db.get(user.id, subscribed_id, )
        if subscription:
            raise SubscribeException(data={'reason': 'You have already subscribed'})
        await self.subscription_db.create(subscribed_id, user.id)

    async def unsubscribe(self,
                          subscribed_id: UUID,
                          user: User):
        if subscribed_id == user.id:
            raise UnSubscribeException(data={'reason': 'You cant unsubscribe to yourself'})
        subscription = await self.subscription_db.get(user.id, subscribed_id, )
        if not subscription:
            raise NonExistentSubscription
        await self.subscription_db.remove(subscribed_id, user.id)

    async def get_user_subscribed(self,
                                  subscriber: User,
                                  subscribed: User):
        return await self.subscription_db.get(subscriber.id, subscribed.id)

    async def get_all_user_subscribed(self,
                                      user: User):
        return await self.subscription_db.get_all_subscribed(user)

    async def get_user_subscribers(self,
                                   user: User):
        return await self.subscription_db.get_subscribers(user)

    async def count_user_subscribers(self,
                                     user: User):
        return len(await self.get_user_subscribers(user))
