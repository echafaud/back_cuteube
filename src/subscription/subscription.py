from fastapi import Depends
from src.database import get_async_db_session
from src.subscription.models import Subscription
from src.subscription.subscription_database_adapter import SubscriptionDatabaseAdapter
from src.subscription.subscription_manager import SubscriptionManager


async def get_subscription_db(db_session=Depends(get_async_db_session)):
    yield SubscriptionDatabaseAdapter(db_session, Subscription)


async def get_subscription_manager(subscription_db=Depends(get_subscription_db)):
    yield SubscriptionManager(subscription_db)
