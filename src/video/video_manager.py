import uuid
from typing import List

from botocore.client import BaseClient

from src.user.models import User
from src.video.exceptions import UploadVideoException, VideoNotExists
from src.video.models import Video
from src.video.shemas import VideoUpload, BaseVideo, VideoView
from src.config import BUCKET_NAME
from src.video.video_database_adapter import VideoDatabaseAdapter


class VideoManager:
    def __init__(self, s3: BaseClient, video_db: VideoDatabaseAdapter):
        self.s3 = s3
        self.video_db = video_db

    async def upload(self, video: VideoUpload, user: User):
        video_id = uuid.uuid4()
        try:
            await self.s3.upload_fileobj(video._video_file.file, BUCKET_NAME, f'videos/{video_id}')
            await self.s3.upload_fileobj(video._preview_file.file, BUCKET_NAME, f'previews/{video_id}')
        except Exception as e:
            raise UploadVideoException(data={"reason": f'{e}'})
        video_model = video.dict()
        video_model["author"] = user.id
        video_model["id"] = video_id
        await self.video_db.create(video_model)

    async def get_latest_videos(self, limit) -> List[Video]:
        result = await self.video_db.get_latest_videos(limit)
        return result

    async def get_video(self, id: uuid.UUID) -> Video:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        return video

    async def get_video_link(self, id: uuid.UUID) -> str:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists

        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'videos/{str(video.id)}'})
        # view_video = BaseVideo.from_orm(video)
        # view_video_dict = view_video.dict()
        # view_video_dict["link"] = link
        return link

    async def get_liked_videos(self, user: User, limit: int):
        return user.liked_videos[:limit]

    async def get_video_likes(self, id: uuid.UUID) -> int:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        return len(video.liked_users)

    async def get_preview_link(self, id: uuid.UUID):
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists

        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'previews/{str(video.id)}'})
        return link

    async def delete(self, user: User, id: uuid.UUID):
        video = await self.video_db.get(id)
        if video.author == user.id:
            await self.video_db.remove(video)
