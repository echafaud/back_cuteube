from src.auth.models import User
from src.subscription.shemas import BaseSubscription
from src.subscription.subscription_database_adapter import SubscriptionDatabaseAdapter


class SubscriptionManager:
    def __init__(self, subscription_db: SubscriptionDatabaseAdapter):
        self.subscription_db = subscription_db

    async def subscribe(self, subscription: BaseSubscription, user: User):
        await self.subscription_db.create(subscription.dict(), user.id)

    async def unsubscribe(self, subscription: BaseSubscription, user: User):
        await self.subscription_db.remove(subscription, user.id)

    async def get_user_subscribed(self, user: User):
        return await self.subscription_db.get_subscribed(user)

    async def get_user_subscribers(self, user: User):
        return await self.subscription_db.get_subscribers(user)
