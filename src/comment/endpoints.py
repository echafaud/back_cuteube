from typing import List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends

from src.comment.comment import get_comment_manager
from src.comment.comment_manager import CommentManager
from src.comment.shemas import CommentCreate, CommentRead, CommentEdit
from src.user.auth import access_user
from src.user.models import User
from src.video.exceptions import NonExistentVideo
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

comment_router = jsonrpc.Entrypoint(path='/api/v1/comment')


@comment_router.method(tags=['comment'])
async def post_comment(comment: CommentCreate,
                       user: User = Depends(access_user),
                       comment_manager: CommentManager = Depends(get_comment_manager),
                       video_manager: VideoManager = Depends(get_video_manager),
                       ) -> CommentRead:
    if not await video_manager.check_existing(comment.video_id):
        raise NonExistentVideo
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
async def get_video_comments(id: UUID,
                             limit: int = 20,
                             pagination: int = 0,
                             video_manager: VideoManager = Depends(get_video_manager),
                             comment_manager: CommentManager = Depends(get_comment_manager)) -> List[CommentRead]:
    video = await video_manager.get(id)
    if not video:
        raise NonExistentVideo
    comments = await comment_manager.get_video_comments(video, limit, pagination)
    return comments
