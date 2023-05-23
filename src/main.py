import uuid
from typing import List

import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import Response

from fastapi import Depends, UploadFile, File

from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode

from src.auth.auth import Settings, advanced_authentication_backend
from src.auth.authenticator import Authenticator
from src.auth.exceptions import LoginBadCredentials
from src.auth.models import User
from src.auth.shemas import UserRead, UserCreate, UserLogin
from src.auth.auth import get_user_manager
from src.auth.user_manager import UserManager
from src.comment.comment import get_comment_manager
from src.comment.comment_manager import CommentManager
from src.comment.shemas import CommentRead, BaseComment, CommentEdit, CommentCreate, CommentRemove
from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.like.shemas import BaseLike
from src.video.shemas import VideoUpload, VideoView
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

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


@Authenticator.load_config
def get_config():
    return Settings()


@api_v1.method(result_model=UserRead)
async def register(
        user_create: UserCreate,
        user_manager: UserManager = Depends(get_user_manager)
):
    created_user = await user_manager.create(user_create, safe=True)

    return created_user


@api_v1.method()
async def login(response: Response,
                credentials: UserLogin,
                user_manager: UserManager = Depends(get_user_manager),
                ) -> UserRead:
    user = await user_manager.authenticate(credentials)
    advanced_authentication_backend.advanced_login(response, user)
    await user_manager.on_after_login(user)
    return user


# authenticator = Authenticator([auth_backend], get_user_manager)
adv_auth = Authenticator(get_user_manager, )

access_user = adv_auth.current_user(token_type="access")

refresh_user = adv_auth.current_user(token_type="refresh")


# curr_user = authenticator.current_user()


@api_v1.method()
async def logout(response: Response, user: User = Depends(access_user),
                 user_manager: UserManager = Depends(get_user_manager),
                 ):
    advanced_authentication_backend.advanced_logout(response, user)
    await user_manager.on_after_logout(user)


@api_v1.method()
async def refresh(response: Response, user: User = Depends(refresh_user),
                  ):
    return advanced_authentication_backend.refresh(response, user)


@api_v1.method()
async def protected(user: User = Depends(access_user)) -> str:
    return user.username


@app.post("/upload_video")
async def upload_video(video: VideoUpload = Depends(),
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)) -> str:
    await video_manager.upload(video, user)
    return video.title


@api_v1.method()
async def get_video(id: uuid.UUID,
                    video_manager: VideoManager = Depends(get_video_manager)) -> VideoView:
    return await video_manager.get_video(id)


@api_v1.method()
async def get_video_link(id: uuid.UUID,
                         video_manager: VideoManager = Depends(get_video_manager)) -> str:
    return await video_manager.get_video_link(id)


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
async def rate(like: BaseLike,
               user: User = Depends(access_user),
               like_manager: LikeManager = Depends(get_like_manager)):
    await like_manager.rate(user, like)


@api_v1.method()
async def remove_rating(like: BaseLike,
                        user: User = Depends(access_user),
                        like_manager: LikeManager = Depends(get_like_manager)):
    await like_manager.remove_rating(user, like)


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
async def remove_comment(comment: CommentRemove,
                         user: User = Depends(access_user),
                         comment_manager: CommentManager = Depends(get_comment_manager)):
    await comment_manager.remove(user, comment)


app.bind_entrypoint(api_v1)
