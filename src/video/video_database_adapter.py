import uuid
from typing import Type, Dict, Any, List

from sqlalchemy import select, Select, delete, Delete, union, union_all, CompoundSelect, and_, or_
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import count

from src.subscription.models import Subscription
from src.user.models import User
from src.video.models import Video, Permission
from src.view.models import View


class VideoDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            video_table: Type[Video],
    ):
        self.session = session
        self.video_table = video_table

    async def create(self, create_dict: Dict[str, Any]):
        video = self.video_table(**create_dict)
        self.session.add(video)
        await self.session.commit()
        return video

    async def update(self, video: Video, update_dict: Dict[str, Any]) -> Video:
        for key, value in update_dict.items():
            setattr(video, key, value)
        self.session.add(video)
        await self.session.commit()
        return video

    async def get(self, id: uuid.UUID) -> Video:
        statement = select(self.video_table).where(self.video_table.id == id)
        return await self._get_video(statement)

    async def get_latest_videos(self, user_permissions: List[Permission], user: User):
        statement = self.get_permission_select(user, user_permissions).order_by(self.video_table.uploaded_at.desc())
        print(statement)
        return await self._get_videos(statement)

    async def get_liked_by_users(self, user_permissions: List[Permission], user: User):
        statement = self.get_permission_select(user, user_permissions).join(self.video_table.liked_users).group_by(
            self.video_table.id).order_by(
            count().desc())
        return await self._get_videos(statement)

    async def get_popular_videos(self, user_permissions: List[Permission], user: User):
        statement = self.get_permission_select(user, user_permissions).join(self.video_table.models_views).where(
            View.viewing_time != None).group_by(
            self.video_table.id).order_by(
            count().desc())
        return await self._get_videos(statement)

    async def get_liked_videos(self, current_user: User):
        liked_videos = await self.session.scalars(current_user.liked_videos)
        return liked_videos.all()

    async def get_viewed_videos(self, current_user: User):
        viewed_videos = await self.session.scalars(current_user.viewed_videos)
        return viewed_videos.all()

    async def get_user_videos(self, requested_user: User, user_permissions: List[Permission], current_user: User):
        statement = self.get_permission_select(current_user, user_permissions, requested_user.videos)
        return await self._get_videos(statement)

    async def get_latest_user_videos(self, requested_user: User,
                                     user_permissions: List[Permission],
                                     current_user: User):
        statement = self.get_permission_select(current_user, user_permissions, requested_user.videos).order_by(
            self.video_table.uploaded_at.desc())
        # statement = select(self.video_table).order_by(self.video_table.upload_at.desc()).where(
        #     requested_user.id == self.video_table.author)
        return await self._get_videos(statement)

    async def get_popular_user_videos(self, requested_user: User,
                                      user_permissions: List[Permission],
                                      current_user: User):
        # statement = select(self.video_table).join(self.video_table.models_views).where(
        #     View.viewing_time != None, requested_user.id == self.video_table.author).group_by(
        #     self.video_table.id).order_by(
        #     count().desc())
        statement = self.get_permission_select(current_user, user_permissions, requested_user.videos).join(
            self.video_table.models_views).where(
            View.viewing_time != None).group_by(self.video_table.id).order_by(count().desc())
        return await self._get_videos(statement)

    async def remove(self, video: Video):
        statement = delete(self.video_table).where(self.video_table.id == video.id)
        await self._remove(statement)

    async def _get_videos(self, statement):
        results = await self.session.execute(statement)
        return results.scalars().unique().all()

    async def _get_video(self, statement: Select):
        results = await self.session.execute(statement)
        return results.scalar_one_or_none()

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()

    def get_permission_select(self, user: User, user_permissions: List[Permission], selected: Select = None):
        if selected is None:
            selected = select(self.video_table)
        return selected \
            .where(or_(self.video_table.permission.in_(user_permissions),
                       and_(self.video_table.permission == Permission.for_myself,
                            self.video_table.owner == user.id),
                       and_(self.video_table.permission == Permission.for_subscribers,
                            or_(user.id == self.video_table.owner,
                                and_(Subscription.subscriber == user.id,
                                     Subscription.subscribed == self.video_table.owner),
                                ))))
