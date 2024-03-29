import uuid
from datetime import timedelta, datetime
from typing import Type, Dict, Any, Optional

from sqlalchemy import select, Select, delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User
from src.video.models import Video
from src.view.models import View, UserView
from src.view.shemas import ViewRead


class ViewDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            view_table: Type[View],
    ):
        self.session = session
        self.view_table = view_table

    async def create(self, create_dict: Dict[str, Any], user_id: Optional[uuid.UUID]):
        view = self.view_table(**create_dict)
        view.owner_id = user_id
        view.fingerprint = view.fingerprint if view.viewing_time else None
        if view.viewing_time is not None and view.viewing_time < timedelta(seconds=15):
            view.viewing_time = None
        self.session.add(view)
        await self.session.commit()
        return view

    async def get_video_views(self, video: Video):
        statement = select(self.view_table).where(
            self.view_table.video_id == video.id, self.view_table.viewing_time != None)
        return await self._get_views(statement)

    async def _get_views(self, statement: Select):
        results = await self.session.execute(statement)
        return results.scalars().all()

    async def get(self, user_view: UserView):
        statement = select(self.view_table).where(
            self.view_table.id == user_view.view_id)
        return await self._get(statement)

    async def _get(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def get_user_video_views(self, user, video_id):
        statement = select(self.view_table).where(
            self.view_table.video_id == video_id, self.view_table.owner_id == user.id,
            self.view_table.viewed_at > datetime.utcnow() - timedelta(hours=24))
        return await self._get_views(statement)

    async def get_viewer_video_views(self, fingerprint, video_id):
        statement = select(self.view_table).where(
            self.view_table.video_id == video_id, self.view_table.fingerprint == fingerprint,
            self.view_table.viewed_at > datetime.utcnow() - timedelta(hours=24))
        return await self._get_views(statement)
