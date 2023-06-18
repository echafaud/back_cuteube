from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth import optional_access_user, access_user
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.user.shemas import UserRead
from src.video.exceptions import NonExistentVideo
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager
from src.view.shemas import BaseView
from src.view.view import get_view_manager
from src.view.view_manager import ViewManager

view_router = jsonrpc.Entrypoint(path='/view')


@view_router.method(tags=['view'])
async def record_view(view: BaseView,
                      user: User = Depends(optional_access_user),
                      view_manager: ViewManager = Depends(get_view_manager),
                      video_manager: VideoManager = Depends(get_video_manager),
                      subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                      ) -> None:
    video = await video_manager.get(view.video_id)
    if not video:
        raise NonExistentVideo
    user_read = user
    if user.id:
        user_read = UserRead.from_orm(user)
        user_read.is_subscribed = await subscription_manager.check_subscription(user_read.id, video.owner)
    if video.permission not in video_manager.get_permissions(user_read, video.owner):
        raise AccessDenied
    await view_manager.record_view(user, view, video)


@view_router.method(tags=['view'])
async def remove_user_view(video_id: UUID,
                           user: User = Depends(access_user),
                           view_manager: ViewManager = Depends(get_view_manager),
                           video_manager: VideoManager = Depends(get_video_manager)
                           ) -> None:
    if not await video_manager.check_existing(video_id):
        raise NonExistentVideo
    await view_manager.remove_user_view(user, video_id)
