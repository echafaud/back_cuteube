import uuid
from typing import Type, Dict, Any

from sqlalchemy import delete, Delete, select, Select
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

    async def create(self, subscribed_id: uuid.UUID, user_id: uuid.UUID):
        subscription = self.subscription_table()
        subscription.subscribed = subscribed_id
        subscription.subscriber = user_id
        self.session.add(subscription)
        await self.session.commit()
        return subscription

    async def remove(self, subscribed_id: uuid.UUID, user_id: uuid.UUID):
        statement = delete(self.subscription_table).where(
            self.subscription_table.subscriber == user_id, self.subscription_table.subscribed == subscribed_id)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()

    async def get_all_subscribed(self, user: User):
        users_subscribed = await self.session.scalars(user.subscribed)
        return users_subscribed.all()

    async def get_subscribers(self, user: User):
        users_subscribers = await self.session.scalars(user.subscribers)
        return users_subscribers.all()

    async def get_subscribed(self, subscriber: User, subscribed: User):
        statement = select(self.subscription_table).where(
            self.subscription_table.subscriber == subscriber.id, self.subscription_table.subscribed == subscribed.id)
        return await self._get(statement)

    async def _get(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
