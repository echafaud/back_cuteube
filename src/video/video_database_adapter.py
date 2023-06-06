import uuid
from typing import Type, Dict, Any

from sqlalchemy import select, Select, delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.video.models import Video


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

    async def get(self, id: uuid.UUID):
        statement = select(self.video_table).where(self.video_table.id == id)
        return await self._get_video(statement)

    async def get_latest_videos(self, limit: int):
        statement = select(self.video_table).order_by(self.video_table.upload_at.desc()).limit(limit)
        return await self._get_videos(statement)

    async def _get_videos(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalars().all()

    async def _get_video(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def remove(self, video: Video):
        statement = delete(self.video_table).where(self.video_table.id == video.id)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()
