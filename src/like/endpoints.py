from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.like.shemas import BaseLike
from src.user.auth import access_user
from src.user.models import User

like_router = jsonrpc.Entrypoint(path='/api/v1/like')


@like_router.method(tags=["like"])
async def rate(like: BaseLike,
               user: User = Depends(access_user),
               like_manager: LikeManager = Depends(get_like_manager)
               ) -> None:
    await like_manager.rate(user, like)
