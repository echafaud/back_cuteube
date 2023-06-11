from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth import access_user
from src.user.exceptions import NonExistentUser
from src.user.models import User
from src.user.user import get_user_manager
from src.user.user_manager import UserManager

subscription_router = jsonrpc.Entrypoint(path='/api/v1/subscription')


@subscription_router.method(tags=['subscription'])
async def subscribe(id: UUID,
                    user: User = Depends(access_user),
                    user_manager: UserManager = Depends(get_user_manager),
                    subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                    ) -> None:
    if not await user_manager.check_existing(id):
        raise NonExistentUser
    await subscription_manager.subscribe(id, user)


@subscription_router.method(tags=['subscription'])
async def unsubscribe(id: UUID,
                      user: User = Depends(access_user),
                      user_manager: UserManager = Depends(get_user_manager),
                      subscription_manager: SubscriptionManager = Depends(get_subscription_manager),

                      ) -> None:
    if not await user_manager.check_existing(id):
        raise NonExistentUser
    await subscription_manager.unsubscribe(id, user)
