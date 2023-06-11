import uuid
from typing import List
from uuid import UUID

import fastapi_jsonrpc as jsonrpc
from fastapi import Depends
from starlette.responses import JSONResponse

from src.user.auth import access_user, optional_access_user
from src.user.models import User
from src.video.shemas import VideoUpload, VideoView
from src.video.video import get_video_manager
from src.video.video_manager import VideoManager

video_router = jsonrpc.Entrypoint(path='/api/v1/video')


@video_router.post('/api/v1/video/upload_video', tags=['video'])
async def upload_video(video: VideoUpload = Depends(),
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)
                       ) -> JSONResponse:
    video = await video_manager.upload(video, user)
    result = video.dict()
    content = {
        'jsonrpc': '2.0',
        'result': result | {"id": str(result["id"]), "author": str(result["author"])},
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
                    ) -> VideoView:
    return await video_manager.get_video_view(id, user)


@video_router.method(tags=['video'])
async def get_video_link(id: uuid.UUID,
                         video_manager: VideoManager = Depends(get_video_manager)
                         ) -> str:
    return await video_manager.get_video_link(id)


@video_router.method(tags=['video'])
async def get_preview_link(id: uuid.UUID,
                           video_manager: VideoManager = Depends(get_video_manager)
                           ) -> str:
    return await video_manager.get_preview_link(id)


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
async def remove_video(id: uuid.UUID,
                       user: User = Depends(access_user),
                       video_manager: VideoManager = Depends(get_video_manager)
                       ) -> None:
    await video_manager.delete(user, id)
