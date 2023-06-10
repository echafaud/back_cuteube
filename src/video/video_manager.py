import uuid
from datetime import timedelta
from typing import List, Optional, Any
from io import BytesIO
from botocore.client import BaseClient
import filetype
from botocore.exceptions import ClientError
from fastapi import UploadFile

from src.like.like_manager import LikeManager
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.video.exceptions import UploadVideoException, VideoNotExists, DeleteVideoException
from src.video.models import Video
from src.video.shemas import VideoUpload, BaseVideo, VideoView
from src.config import BUCKET_NAME
from src.video.video_database_adapter import VideoDatabaseAdapter
from src.view.view_manager import ViewManager
from pymediainfo import MediaInfo


class VideoManager:
    max_video_size = 100
    max_preview_size = 10
    max_title_len = 100
    max_description_len = 5000

    def __init__(self,
                 s3: BaseClient,
                 video_db: VideoDatabaseAdapter,
                 view_manager: ViewManager,
                 like_manager: LikeManager):
        self.s3 = s3
        self.video_db = video_db
        self.view_manager = view_manager
        self.like_manager = like_manager

    async def get(self,
                  id: uuid.UUID
                  ) -> Optional[Video]:
        return await self.video_db.get(id)

    async def get_video_view(self,
                             id: uuid.UUID,
                             curren_user: User = None
                             ) -> VideoView:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        return await self.convert_video_to_video_view(video, curren_user)

    async def convert_video_to_video_view(self,
                                          video: Video,
                                          current_user: User = None
                                          ) -> VideoView:
        video_view = VideoView.from_orm(video)
        video_view.likes = await self.like_manager.count_video_likes(video)
        video_view.dislikes = await self.like_manager.count_video_dislikes(video)
        video_view.views = await self.view_manager.count_video_views(video)
        if current_user and current_user.id:
            user_view = await self.view_manager.get_user_view(current_user, video)
            if user_view:
                video_view.stop_timecode = user_view.stop_timecode
            like = await self.like_manager.get_rate(current_user, video)
            video_view.like = like.status if like else like
        return video_view

    async def upload(self,
                     video: VideoUpload,
                     user: User
                     ) -> VideoView:

        # with BytesIO() as copied_file:
        #     copied_file.write(await video._video_file.read())
        #     video_media_info = MediaInfo.parse(UploadFile(copied_file).file)
        #     preview_media_info = MediaInfo.parse(video._preview_file.file)
        #     self._validate(video, video_media_info, preview_media_info)
        #     await video._video_file.seek(0)
        video_media_info = MediaInfo.parse(video._video_file.file)
        preview_media_info = MediaInfo.parse(video._preview_file.file)
        self._validate(video, video_media_info, preview_media_info)
        await video._video_file.seek(0)
        await video._preview_file.seek(0)

        video_head = None
        video_id = uuid.uuid4()

        try:
            await self.s3.upload_fileobj(video._video_file.file, BUCKET_NAME, f'videos/{video_id}')
            await self.s3.upload_fileobj(video._preview_file.file, BUCKET_NAME, f'previews/{video_id}')
        except ClientError:
            pass

        try:
            video_head = await self.s3.head_object(Bucket=BUCKET_NAME, Key=f'videos/{video_id}')
            await self.s3.head_object(Bucket=BUCKET_NAME, Key=f'previews/{video_id}')
        except ClientError:
            while video_head:
                response = await self.s3.delete_object(Bucket=BUCKET_NAME, Key='videos/{video_id}')
                if response["DeleteMarker"]:
                    break
            raise UploadVideoException(data={"reason": 'Failed to upload files to s3'})

        video = await self.video_db.create(video.dict()
                                           | {'id': video_id,
                                              "author": user.id,
                                              "duration": timedelta(
                                                  milliseconds=video_media_info.general_tracks[0].duration)})
        return VideoView.from_orm(video)

    async def get_video_link(self,
                             id: uuid.UUID
                             ) -> str:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'videos/{str(video.id)}'})
        return link

    async def get_preview_link(self,
                               id: uuid.UUID
                               ) -> str:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'previews/{str(video.id)}'})
        return link

    async def get_latest_videos(self,
                                current_user: User,
                                limit: int,
                                pagination: int,
                                ) -> List[VideoView]:
        latest_videos = await self.video_db.get_latest_videos()
        paginated_result = self._paginate(limit, pagination, latest_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_liked_videos(self,
                               current_user: User,
                               limit: int,
                               pagination: int,
                               ) -> List[VideoView]:
        liked_videos = await self.video_db.get_liked_videos(current_user)
        paginated_result = self._paginate(limit, pagination, liked_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def count_video_likes(self,
                                id: uuid.UUID
                                ) -> int:
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        return len(video.liked_users)

    async def delete(self,
                     user: User,
                     id: uuid.UUID):
        video = await self.video_db.get(id)
        if video is None:
            raise VideoNotExists
        if video.author != user.id:
            raise AccessDenied
        try:
            video_response = await self.s3.delete_object(Bucket=BUCKET_NAME, Key=f'videos/{str(video.id)}')
            preview_response = await self.s3.delete_object(Bucket=BUCKET_NAME, Key=f'previews/{str(video.id)}')
            if not video_response["DeleteMarker"] or not preview_response["DeleteMarker"]:
                raise DeleteVideoException
        except ClientError:
            raise DeleteVideoException

        await self.video_db.remove(video)

    def _paginate(self,
                  limit,
                  pagination,
                  result) -> List[Any]:
        return result[limit * pagination: limit * (pagination + 1)]

    def _validate(self,
                  video: VideoUpload,
                  video_media_info,
                  preview_media_info):
        if len(video.title) > self.max_title_len:
            raise UploadVideoException(
                data={"reason": f'Title must contain no more than {self.max_title_len} characters'})
        elif len(video.description) > self.max_description_len:
            raise UploadVideoException(
                data={"reason": f'Description must contain no more than {self.max_description_len} characters'})
        elif not video_media_info.video_tracks[0]:
            raise UploadVideoException(data={"reason": 'Uploaded file is not a video or this format is not supported'})
        elif not preview_media_info.image_tracks[0]:
            raise UploadVideoException(data={"reason": 'Uploaded file is not a image or this format is not supported'})
        elif video_media_info.general_tracks[0].file_size / (1024 * 1024) > self.max_video_size:
            raise UploadVideoException(
                data={"reason": f'Exceeded the maximum video size. Max.size = {self.max_video_size}mb'})
        elif preview_media_info.general_tracks[0].file_size / (1024 * 1024) > self.max_preview_size:
            raise UploadVideoException(
                data={"reason": f'Exceeded the maximum preview size. Max.size = {self.max_preview_size}mb'})
