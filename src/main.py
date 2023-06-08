import uuid
from typing import List, Optional

import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from fastapi import Depends, UploadFile, File

from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from src.user.auth import Settings, advanced_authentication_backend
from src.user.authenticator import Authenticator
from src.user.endpoints import user_router
from src.user.exceptions import LoginBadCredentials
from src.user.models import User
from src.user.shemas import UserRead, UserCreate, UserLogin
from src.user.user import get_auth_user_manager, get_user_manager
from src.user.auth_user_manager import AuthUserManager
from src.comment.comment import get_comment_manager
from src.comment.comment_manager import CommentManager
from src.comment.shemas import CommentRead, BaseComment, CommentEdit, CommentCreate, CommentRemove
from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.like.shemas import BaseLike
from src.subscription.shemas import BaseSubscription
from src.subscription.subscription import get_subscription_manager
from src.subscription.subscription_manager import SubscriptionManager
from src.user.user_manager import UserManager
from src.video.shemas import VideoUpload, VideoView
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager
from src.view.shemas import BaseView, ViewRead, ViewRemove
from src.view.view import get_view_manager
from src.view.view_manager import ViewManager

app = jsonrpc.API()
api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "X-CSRF-Token"],
)

adv_auth = Authenticator(get_auth_user_manager, )

access_user = adv_auth.authenticate_current_user(token_type="access")

refresh_user = adv_auth.authenticate_current_user(token_type="refresh")
optional_access_user = adv_auth.authenticate_current_user(token_type="access", optional=True)


@api_v1.method()
async def protected(user: User = Depends(access_user)) -> str:
    return user.username


@api_v1.method()
async def optional_protected(user: User = Depends(optional_access_user)) -> Optional[str]:
    return user.username


@app.post("/upload_video")
async def upload_video(video: VideoUpload = Depends(),
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)) -> str:
    await video_manager.upload(video, user)
    return video.title


@api_v1.method()
async def get_video(id: uuid.UUID,
                    user: User = Depends(optional_access_user),
                    video_manager: VideoManager = Depends(get_video_manager),
                    view_manager: ViewManager = Depends(get_view_manager),
                    like_manager: LikeManager = Depends(get_like_manager)
                    ) -> VideoView:
    video = await video_manager.get_video(id)
    video_view = VideoView.from_orm(video)
    video_view.likes = await like_manager.count_video_likes(video)
    video_view.dislikes = await like_manager.count_video_dislikes(video)
    video_view.views = await view_manager.count_video_views(video)
    if user.id:
        user_view = await view_manager.get_user_view(user, video)
        if user_view:
            video_view.stop_timecode = user_view.stop_timecode
        like = await like_manager.get_rate(user, video)
        video_view.like = like.status if like else like

    return video_view


@api_v1.method()
async def get_video_link(id: uuid.UUID,
                         video_manager: VideoManager = Depends(get_video_manager)) -> str:
    return await video_manager.get_video_link(id)


@api_v1.method()
async def get_preview_link(id: uuid.UUID,
                           video_manager: VideoManager = Depends(get_video_manager)) -> str:
    return await video_manager.get_preview_link(id)


@api_v1.method()
async def get_latest_videos(limit: int = 10,
                            video_manager: VideoManager = Depends(get_video_manager)) -> List[VideoView]:
    return await video_manager.get_latest_videos(limit)


@api_v1.method()
async def get_liked_videos(limit: int = 10,
                           user: User = Depends(access_user),
                           video_manager: VideoManager = Depends(get_video_manager)) -> List[VideoView]:
    return await video_manager.get_liked_videos(user, limit)


@api_v1.method()
async def get_video_likes(id: uuid.UUID, video_manager: VideoManager = Depends(get_video_manager)) -> int:
    return await video_manager.get_video_likes(id)


@api_v1.method()
async def remove_video(id: uuid.UUID,
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)):
    await video_manager.delete(user, id)


@api_v1.method()
async def rate(like: BaseLike,
               user: User = Depends(access_user),
               like_manager: LikeManager = Depends(get_like_manager)):
    await like_manager.rate(user, like)


@api_v1.method()
async def remove_rating(id: uuid.UUID,
                        user: User = Depends(access_user),
                        like_manager: LikeManager = Depends(get_like_manager)):
    await like_manager.remove_rating(user, id)


@api_v1.method()
async def post_comment(comment: CommentCreate,
                       user: User = Depends(access_user),
                       comment_manager: CommentManager = Depends(get_comment_manager)) -> CommentRead:
    return await comment_manager.post(user, comment)


@api_v1.method()
async def edit_comment(comment: CommentEdit,
                       user: User = Depends(access_user),
                       comment_manager: CommentManager = Depends(get_comment_manager)) -> CommentRead:
    return await comment_manager.edit(user, comment)


@api_v1.method()
async def remove_comment(id: uuid.UUID,
                         user: User = Depends(access_user),
                         comment_manager: CommentManager = Depends(get_comment_manager)):
    await comment_manager.remove(user, id)


@api_v1.method()
async def get_video_comments(id: uuid.UUID,
                             video_manager: VideoManager = Depends(get_video_manager),
                             comment_manager: CommentManager = Depends(get_comment_manager)) -> List[CommentRead]:
    video = await video_manager.get_video(id)
    comments = await comment_manager.get_video_comments(video)
    return comments


@api_v1.method()
async def record_view(view: BaseView,
                      user: User = Depends(optional_access_user),
                      view_manager: ViewManager = Depends(get_view_manager)):
    await view_manager.record_view(user, view)


@api_v1.method()
async def remove_view(view: ViewRemove,
                      user: User = Depends(access_user),
                      view_manager: ViewManager = Depends(get_view_manager)):
    await view_manager.remove_user_view(user, view)


@api_v1.method()
async def subscribe(id: uuid.UUID,
                    user: User = Depends(access_user),
                    subscription_manager: SubscriptionManager = Depends(get_subscription_manager)):
    await subscription_manager.subscribe(id, user)


@api_v1.method()
async def unsubscribe(id: uuid.UUID,
                      user: User = Depends(access_user),
                      subscription_manager: SubscriptionManager = Depends(get_subscription_manager)):
    await subscription_manager.unsubscribe(id, user)


@api_v1.method()
async def get_all_user_subscribed(
        user: User = Depends(access_user),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager)) -> List[UserRead]:
    return await subscription_manager.get_all_user_subscribed(user)


@api_v1.method()
async def get_user_subscribers(
        user: User = Depends(access_user),
        subscription_manager: SubscriptionManager = Depends(get_subscription_manager)) -> List[UserRead]:
    return await subscription_manager.get_user_subscribers(user)


@api_v1.method()
async def count_user_subscribers(id: uuid.UUID,
                                 user_manager: AuthUserManager = Depends(get_auth_user_manager),
                                 subscription_manager: SubscriptionManager = Depends(get_subscription_manager)) -> int:
    return await subscription_manager.count_user_subscribers(await user_manager.get(id))


app.bind_entrypoint(api_v1)
app.bind_entrypoint(user_router)
