import uuid
from typing import List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends
from starlette.responses import JSONResponse

from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth import access_user, optional_access_user, access_superuser
from src.user.exceptions import NonExistentUser
from src.user.models import User
from src.user.shemas import UserRead
from src.user.user import get_user_manager
from src.user.user_manager import UserManager
from src.video.exceptions import NonExistentVideo
from src.video.shemas import VideoUpload, VideoView
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

video_router = jsonrpc.Entrypoint(path='/video')


@video_router.post('/video/upload_video', tags=['video'])
async def upload_video(video: VideoUpload = Depends(),
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)
                       ) -> JSONResponse:
    video = await video_manager.upload(video, user)
    result = video.dict()
    content = {
        'jsonrpc': '2.0',
        'result': result | {"id": str(result["id"]),
                            "owner": str(result["owner"]),
                            "uploaded_at": result["uploaded_at"].strftime('%m-%d-%Y')},
        'id': None
    }
    return JSONResponse(
        status_code=200,
        content=content,
    )


@video_router.method(tags=['video'])
async def get_video(id: UUID,
                    user: User = Depends(optional_access_user),
                    video_manager: VideoManager = Depends(get_video_manager),
                    subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                    ) -> VideoView:
    video = await video_manager.get(id)
    if video is None:
        raise NonExistentVideo
    if user.id:
        user = UserRead.from_orm(user)
        user.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    return await video_manager.get_video_view(video, user)


@video_router.method(tags=['video'])
async def get_video_link(id: uuid.UUID,
                         user: User = Depends(optional_access_user),
                         video_manager: VideoManager = Depends(get_video_manager),
                         subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                         ) -> str:
    video = await video_manager.get(id)
    if video is None:
        raise NonExistentVideo
    if user.id:
        user = UserRead.from_orm(user)
        user.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    return await video_manager.get_video_link(video, user)


@video_router.method(tags=['video'])
async def get_preview_link(id: uuid.UUID,
                           user: User = Depends(optional_access_user),
                           video_manager: VideoManager = Depends(get_video_manager),
                           subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                           ) -> str:
    video = await video_manager.get(id)
    if video is None:
        raise NonExistentVideo
    if user.id:
        user = UserRead.from_orm(user)
        user.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    return await video_manager.get_preview_link(video, user)


@video_router.method(tags=['video'])
async def get_latest_videos(limit: int = 20,
                            pagination: int = 0,
                            user: User = Depends(optional_access_user),
                            video_manager: VideoManager = Depends(get_video_manager)
                            ) -> List[VideoView]:
    return await video_manager.get_latest_videos(user, limit, pagination)


@video_router.method(tags=['video'])
async def get_liked_videos(limit: int = 20,
                           pagination: int = 0,
                           user: User = Depends(access_user),
                           video_manager: VideoManager = Depends(get_video_manager)
                           ) -> List[VideoView]:
    return await video_manager.get_liked_videos(user, limit, pagination)


@video_router.method(tags=['video'])
async def get_liked_by_users(limit: int = 20,
                             pagination: int = 0,
                             user: User = Depends(optional_access_user),
                             video_manager: VideoManager = Depends(get_video_manager)
                             ) -> List[VideoView]:
    return await video_manager.get_liked_by_users(user, limit, pagination)


@video_router.method(tags=['video'])
async def get_popular_videos(limit: int = 20,
                             pagination: int = 0,
                             user: User = Depends(optional_access_user),
                             video_manager: VideoManager = Depends(get_video_manager)
                             ) -> List[VideoView]:
    return await video_manager.get_popular_videos(user, limit, pagination)


@video_router.method(tags=['video'])
async def get_viewed_videos(limit: int = 20,
                            pagination: int = 0,
                            user: User = Depends(access_user),
                            video_manager: VideoManager = Depends(get_video_manager)
                            ) -> List[VideoView]:
    return await video_manager.get_viewed_videos(user, limit, pagination)


@video_router.method(tags=['video'])
async def get_user_videos(id: UUID,
                          limit: int = 20,
                          pagination: int = 0,
                          current_user: User = Depends(optional_access_user),
                          user_manager: UserManager = Depends(get_user_manager),
                          video_manager: VideoManager = Depends(get_video_manager)
                          ) -> List[VideoView]:
    requested_user = await user_manager.get(id)
    if not requested_user:
        raise NonExistentUser
    return await video_manager.get_user_videos(current_user, requested_user, limit, pagination)


@video_router.method(tags=['video'])
async def get_latest_user_videos(id: UUID,
                                 limit: int = 20,
                                 pagination: int = 0,
                                 current_user: User = Depends(optional_access_user),
                                 user_manager: UserManager = Depends(get_user_manager),
                                 video_manager: VideoManager = Depends(get_video_manager)
                                 ) -> List[VideoView]:
    requested_user = await user_manager.get(id)
    if not requested_user:
        raise NonExistentUser
    return await video_manager.get_latest_user_videos(current_user, requested_user, limit, pagination)


@video_router.method(tags=['video'])
async def get_popular_user_videos(id: UUID,
                                  limit: int = 20,
                                  pagination: int = 0,
                                  current_user: User = Depends(optional_access_user),
                                  user_manager: UserManager = Depends(get_user_manager),
                                  video_manager: VideoManager = Depends(get_video_manager)
                                  ) -> List[VideoView]:
    requested_user = await user_manager.get(id)
    if not requested_user:
        raise NonExistentUser
    return await video_manager.get_popular_user_videos(current_user, requested_user, limit, pagination)


@video_router.method(tags=['video'])
async def remove_video(id: uuid.UUID,
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)
                       ) -> None:
    await video_manager.delete(user, id)


@video_router.method(tags=['video'])
async def admin_remove_video(id: uuid.UUID,
                             user: User = Depends(access_superuser),
                             video_manager: VideoManager = Depends(get_video_manager)
                             ) -> None:
    await video_manager.admin_delete(user, id)
