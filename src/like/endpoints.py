from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.like.shemas import BaseLike
from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth import access_user
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.user.shemas import UserRead
from src.video.exceptions import NonExistentVideo
from src.video.models import Permission
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

like_router = jsonrpc.Entrypoint(path='/like')


@like_router.method(tags=["like"])
async def rate(like: BaseLike,
               user: User = Depends(access_user),
               like_manager: LikeManager = Depends(get_like_manager),
               video_manager: VideoManager = Depends(get_video_manager),
               subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
               ) -> None:
    video = await video_manager.get(like.video_id)
    if not video:
        raise NonExistentVideo
    user_read = UserRead.from_orm(user)
    user_read.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    if video.permission not in video_manager.get_permissions(user_read, video.owner):
        raise AccessDenied
    await like_manager.rate(user, like)
