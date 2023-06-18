from typing import List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.comment.comment import get_comment_manager
from src.comment.comment_manager import CommentManager
from src.comment.shemas import CommentCreate, CommentRead, CommentEdit
from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.auth import access_user, optional_access_user, access_superuser
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.user.shemas import UserRead
from src.video.exceptions import NonExistentVideo
from src.video.models import Permission
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

comment_router = jsonrpc.Entrypoint(path='/comment')


@comment_router.method(tags=['comment'])
async def post_comment(comment: CommentCreate,
                       user: User = Depends(access_user),
                       comment_manager: CommentManager = Depends(get_comment_manager),
                       video_manager: VideoManager = Depends(get_video_manager),
                       subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                       ) -> CommentRead:
    video = await video_manager.get(comment.video_id)
    if not video:
        raise NonExistentVideo
    user_read = UserRead.from_orm(user)
    user_read.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    if video.permission not in video_manager.get_permissions(user_read, video.owner):
        raise AccessDenied
    return await comment_manager.post(user, comment)


@comment_router.method(tags=['comment'])
async def edit_comment(comment: CommentEdit,
                       user: User = Depends(access_user),
                       comment_manager: CommentManager = Depends(get_comment_manager)
                       ) -> CommentRead:
    return await comment_manager.edit(user, comment)


@comment_router.method(tags=['comment'])
async def remove_comment(id: UUID,
                         user: User = Depends(access_user),
                         comment_manager: CommentManager = Depends(get_comment_manager)):
    await comment_manager.remove(user, id)


@comment_router.method(tags=['comment'])
async def admin_remove_comment(id: UUID,
                               user: User = Depends(access_superuser),
                               comment_manager: CommentManager = Depends(get_comment_manager)):
    await comment_manager.admin_remove(user, id)


@comment_router.method(tags=['comment'])
async def get_video_comments(id: UUID,
                             limit: int = 20,
                             pagination: int = 0,
                             user: User = Depends(optional_access_user),
                             video_manager: VideoManager = Depends(get_video_manager),
                             comment_manager: CommentManager = Depends(get_comment_manager),
                             subscription_manager: SubscriptionManager = Depends(get_subscription_manager),
                             ) -> List[CommentRead]:
    video = await video_manager.get(id)
    if not video:
        raise NonExistentVideo
    if user.id:
        user = UserRead.from_orm(user)
        user.is_subscribed = await subscription_manager.check_subscription(user.id, video.owner)
    if video.permission not in video_manager.get_permissions(user, video.owner):
        raise AccessDenied
    comments = await comment_manager.get_video_comments(video, limit, pagination)
    return comments
