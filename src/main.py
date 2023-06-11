import uuid
from typing import List, Optional

import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response, JSONResponse

from fastapi import Depends, UploadFile, File

from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode
from fastapi import Request

from src.comment.endpoints import comment_router
from src.like.endpoints import like_router
from src.user.auth import Settings, advanced_authentication_backend
from src.user.authenticator import Authenticator
from src.user.endpoints import user_router
from src.user.exceptions import LoginBadCredentials, AccessDenied
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
from src.video.endpoints import video_router
from src.video.exceptions import UploadVideoException
from src.video.shemas import VideoUpload, VideoView
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager
from src.view.endpoints import view_router
from src.view.shemas import BaseView, ViewRead
from src.view.view import get_view_manager
from src.view.view_manager import ViewManager

app = jsonrpc.API()
api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')

origins = [
    "http://localhost:5173",
]


def error_handler(request: Request, exc: jsonrpc.BaseError):
    content = exc.get_resp()
    return JSONResponse(
        status_code=200,
        content=content,
    )


app.add_exception_handler(AccessDenied, error_handler)
app.add_exception_handler(UploadVideoException, error_handler)

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
app.bind_entrypoint(video_router)
app.bind_entrypoint(like_router)
app.bind_entrypoint(comment_router)
app.bind_entrypoint(view_router)
