import uuid
from typing import AsyncGenerator

import aioboto3
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import BOTO_SERVICE_NAME, BOTO_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from src.database import get_async_db_session
from src.like.like import get_like_manager
from src.like.like_manager import LikeManager
from src.video.models import Video
from src.video.video_database_adapter import VideoDatabaseAdapter
from src.video.video_manager import VideoManager
from src.view.view import get_view_manager
from src.view.view_manager import ViewManager

s3_session = aioboto3.Session()


async def get_async_s3_session():
    async with s3_session.client(
            service_name=BOTO_SERVICE_NAME,
            endpoint_url=BOTO_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    ) as session:
        yield session


async def get_video_db(db_session=Depends(get_async_db_session)):
    yield VideoDatabaseAdapter(db_session, Video)


async def get_video_manager(s3=Depends(get_async_s3_session),
                            video_db=Depends(get_video_db),
                            view_manager: ViewManager = Depends(get_view_manager),
                            like_manager: LikeManager = Depends(get_like_manager)):
    yield VideoManager(s3, video_db, view_manager, like_manager)
