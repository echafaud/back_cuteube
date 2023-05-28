import uuid
from select import select
from typing import Type, Dict, Any

from sqlalchemy import delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.subscription.models import Subscription
from src.subscription.shemas import BaseSubscription


class SubscriptionDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            subscription_table: Type[Subscription],
    ):
        self.session = session
        self.subscription_table = subscription_table

    async def create(self, create_dict: Dict[str, Any], user_id: uuid.UUID):
        subscription = self.subscription_table(**create_dict)
        subscription.subscriber = user_id
        self.session.add(subscription)
        await self.session.commit()
        return subscription

    async def remove(self, subscription: BaseSubscription, user_id: uuid.UUID):
        statement = delete(self.subscription_table).where(
            self.subscription_table.subscriber == user_id
            and self.subscription_table.subscribed == subscription.subscribed)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()

    async def get_subscribed(self, user: User):
        users_subscribed = await self.session.scalars(user.subscribed)
        return users_subscribed.all()

    async def get_subscribers(self, user: User):
        users_subscribers = await self.session.scalars(user.subscribers)
        return users_subscribers.all()
