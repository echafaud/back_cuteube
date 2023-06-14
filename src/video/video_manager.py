from uuid import UUID
import uuid
from datetime import timedelta
from typing import List, Optional, Any, Union
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from src.like.like_manager import LikeManager
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.user.shemas import UserRead
from src.video.exceptions import UploadVideoException, NonExistentVideo, DeleteVideoException, NonExistentPermission
from src.video.models import Video, Permission
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
                  id: UUID
                  ) -> Optional[Video]:
        return await self.video_db.get(id)

    async def get_video_view(self,
                             video: Video,
                             current_user: Union[User, UserRead] = None,
                             ) -> VideoView:
        current_user_permissions = self.get_permissions(current_user, video.author)
        if video.permission not in current_user_permissions:
            raise AccessDenied
        return await self.convert_video_to_video_view(video, current_user)

    async def convert_video_to_video_view(self,
                                          video: Video,
                                          current_user: User = None
                                          ) -> VideoView:
        video.permission = video.permission.name
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
                                              'permission': Permission[video.permission],
                                              "duration": timedelta(
                                                  milliseconds=video_media_info.general_tracks[0].duration)})
        video.permission = video.permission.name
        return VideoView.from_orm(video)

    async def get_video_link(self,
                             video: Video,
                             current_user: UserRead
                             ) -> str:
        current_user_permissions = self.get_permissions(current_user, video.author)
        if video.permission not in current_user_permissions:
            raise AccessDenied
        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'videos/{str(video.id)}'})
        return link

    async def get_preview_link(self,
                               video: Video,
                               current_user: UserRead
                               ) -> str:
        current_user_permissions = self.get_permissions(current_user, video.author)
        if video.permission not in current_user_permissions:
            raise AccessDenied
        link = await self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': BUCKET_NAME,
                                                            'Key': f'previews/{str(video.id)}'})
        return link

    async def get_latest_videos(self,
                                current_user: User,
                                limit: int,
                                pagination: int,
                                ) -> List[VideoView]:
        current_user_permissions = self.get_permissions(current_user)
        latest_videos = await self.video_db.get_latest_videos(current_user_permissions, current_user)
        paginated_result = self._paginate(limit, pagination, latest_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_liked_by_users(self,
                                 current_user: User,
                                 limit: int,
                                 pagination: int
                                 ):
        current_user_permissions = self.get_permissions(current_user)
        liked_by_users_videos = await self.video_db.get_liked_by_users(current_user_permissions, current_user)
        paginated_result = self._paginate(limit, pagination, liked_by_users_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_popular_videos(self,
                                 current_user: User,
                                 limit: int,
                                 pagination: int,
                                 ) -> List[VideoView]:
        current_user_permissions = self.get_permissions(current_user)
        popular_videos = await self.video_db.get_popular_videos(current_user_permissions, current_user)
        paginated_result = self._paginate(limit, pagination, popular_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_liked_videos(self,
                               current_user: User,
                               limit: int,
                               pagination: int,
                               ) -> List[VideoView]:
        liked_videos = await self.video_db.get_liked_videos(current_user)
        paginated_result = self._paginate(limit, pagination, liked_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_viewed_videos(self, current_user: User,
                                limit: int,
                                pagination: int,
                                ) -> List[VideoView]:
        viewed_videos = await self.video_db.get_viewed_videos(current_user)
        paginated_result = self._paginate(limit, pagination, viewed_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_user_videos(self, current_user: User,
                              requested_user: User,
                              limit: int,
                              pagination: int,
                              ) -> List[VideoView]:
        current_user_permissions = self.get_permissions(current_user)
        user_videos = await self.video_db.get_user_videos(requested_user, current_user_permissions, current_user)
        paginated_result = self._paginate(limit, pagination, user_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_latest_user_videos(self, current_user: User,
                                     requested_user: User,
                                     limit: int,
                                     pagination: int,
                                     ) -> List[VideoView]:
        current_user_permissions = self.get_permissions(current_user)
        latest_user_videos = await self.video_db.get_latest_user_videos(requested_user, current_user_permissions,
                                                                        current_user)
        paginated_result = self._paginate(limit, pagination, latest_user_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def get_popular_user_videos(self, current_user: User,
                                      requested_user: User,
                                      limit: int,
                                      pagination: int,
                                      ) -> List[VideoView]:
        current_user_permissions = self.get_permissions(current_user)
        popular_user_videos = await self.video_db.get_popular_user_videos(requested_user, current_user_permissions,
                                                                          current_user)
        paginated_result = self._paginate(limit, pagination, popular_user_videos)
        return [await self.convert_video_to_video_view(video, current_user) for video in paginated_result]

    async def count_video_likes(self,
                                id: UUID
                                ) -> int:
        video = await self.video_db.get(id)
        if video is None:
            raise NonExistentVideo
        return len(video.liked_users)

    async def delete(self,
                     user: User,
                     id: UUID):
        video = await self.video_db.get(id)
        if video is None:
            raise NonExistentVideo
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

    async def check_existing(self,
                             video_id
                             ) -> bool:
        video = await self.video_db.get(video_id)
        return True if video else False

    def get_permissions(self,
                        current_user: Union[UserRead, User],
                        video_author: Optional[UUID] = None
                        ) -> List[Permission]:
        current_permissions = [Permission.for_everyone]
        if current_user.id:
            current_permissions.append(Permission.for_authorized)
        if isinstance(current_user,
                      UserRead) and current_user.is_subscribed or video_author and current_user.id == video_author:
            current_permissions.append(Permission.for_subscribers)
        if video_author and current_user.id == video_author:
            current_permissions.append(Permission.for_myself)
        return current_permissions

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
        elif video.permission not in Permission.__members__:
            raise NonExistentPermission
        elif not video_media_info.video_tracks:
            raise UploadVideoException(data={"reason": 'Uploaded file is not a video or this format is not supported'})
        elif not preview_media_info.image_tracks:
            raise UploadVideoException(data={"reason": 'Uploaded file is not a image or this format is not supported'})
        elif video_media_info.general_tracks[0].file_size / (1024 * 1024) > self.max_video_size:
            raise UploadVideoException(
                data={"reason": f'Exceeded the maximum video size. Max.size = {self.max_video_size}mb'})
        elif preview_media_info.general_tracks[0].file_size / (1024 * 1024) > self.max_preview_size:
            raise UploadVideoException(
                data={"reason": f'Exceeded the maximum preview size. Max.size = {self.max_preview_size}mb'})
