from typing import List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends
from starlette.responses import Response

from src.user.auth import advanced_authentication_backend, access_user, refresh_user, optional_access_user
from src.user.exceptions import NonExistentUser, UserVerifyException
from src.user.models import User
from src.user.shemas import UserCreate, UserRead, UserLogin
from src.user.user import get_user_manager
from src.user.user_manager import UserManager

user_router = jsonrpc.Entrypoint(path='/api/v1/user')


@user_router.method(tags=['user'])
async def register(user_create: UserCreate,
                   user_manager: UserManager = Depends(get_user_manager)
                   ) -> UserRead:
    created_user = await user_manager.create(user_create)
    return created_user


@user_router.method(tags=['user'])
async def login(response: Response,
                credentials: UserLogin,
                user_manager: UserManager = Depends(get_user_manager),
                ) -> UserRead:
    user = await user_manager.authenticate(credentials)
    advanced_authentication_backend.advanced_login(response, user)
    await user_manager.on_after_login(user)
    return user


@user_router.method(tags=['user'])
async def logout(response: Response,
                 user: User = Depends(access_user),
                 user_manager: UserManager = Depends(get_user_manager),
                 ) -> None:
    advanced_authentication_backend.advanced_logout(response)
    await user_manager.on_after_logout(user)


@user_router.method(tags=['user'])
async def refresh(response: Response,
                  user: User = Depends(refresh_user),
                  ) -> None:
    return advanced_authentication_backend.refresh(response, user)


@user_router.method(tags=['user'])
async def verify(id: UUID,
                 token: UUID,
                 user_manager: UserManager = Depends(get_user_manager),
                 ) -> None:
    await user_manager.verify(id, token)


@user_router.method(tags=['user'])
async def update_verify(id: UUID,
                        user_manager: UserManager = Depends(get_user_manager),
                        ) -> None:
    await user_manager.update_verify(id)


@user_router.method(tags=['user'])
async def get_user(id: UUID,
                   user: User = Depends(optional_access_user),
                   user_manager: UserManager = Depends(get_user_manager),
                   ) -> UserRead:
    return await user_manager.get_user_read(id, user)


@user_router.method(tags=['user'])
async def get_subscribed(limit: int = 20,
                         pagination: int = 0,
                         user: User = Depends(access_user),
                         user_manager: UserManager = Depends(get_user_manager),
                         ) -> List[UserRead]:
    return await user_manager.get_subscribed(limit, pagination, user)

# @user_router.method(tags=['user'])
# async def get_user_subscribers(
#         user: User = Depends(access_user),
#         subscription_manager: SubscriptionManager = Depends(get_subscription_manager)) -> List[UserRead]:
#     return await subscription_manager.get_user_subscribers(user)
