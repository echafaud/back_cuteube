import uuid

from src.user.models import User
from src.subscription.shemas import BaseSubscription
from src.subscription.subscription_database_adapter import SubscriptionDatabaseAdapter


class SubscriptionManager:
    def __init__(self, subscription_db: SubscriptionDatabaseAdapter):
        self.subscription_db = subscription_db

    async def subscribe(self, subscribed_id: uuid.UUID, user: User):
        if subscribed_id != user.id:
            await self.subscription_db.create(subscribed_id, user.id)

    async def unsubscribe(self, subscribed_id: uuid.UUID, user: User):
        await self.subscription_db.remove(subscribed_id, user.id)

    async def get_user_subscribed(self, subscriber: User, subscribed: User):
        return await self.subscription_db.get_subscribed(subscriber, subscribed)

    async def get_all_user_subscribed(self, user: User):
        return await self.subscription_db.get_all_subscribed(user)

    async def get_user_subscribers(self, user: User):
        return await self.subscription_db.get_subscribers(user)

    async def count_user_subscribers(self, user: User):
        return len(await self.get_user_subscribers(user))
