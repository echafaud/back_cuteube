from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.like.shemas import BaseLike
from src.user.auth import access_user
from src.user.models import User
from src.video.exceptions import NonExistentVideo
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

like_router = jsonrpc.Entrypoint(path='/api/v1/like')


@like_router.method(tags=["like"])
async def rate(like: BaseLike,
               user: User = Depends(access_user),
               like_manager: LikeManager = Depends(get_like_manager),
               video_manager: VideoManager = Depends(get_video_manager),
               ) -> None:
    if not await video_manager.check_existing(like.video_id):
        raise NonExistentVideo
    await like_manager.rate(user, like)
