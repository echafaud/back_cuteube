import uuid
from typing import Type, Dict, Any

from sqlalchemy import select, Select, delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.like.models import Like
from src.user.models import User
from src.video.models import Video


class LikeDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            like_table: Type[Like],
    ):
        self.session = session
        self.like_table = like_table

    async def create(self, create_dict: Dict[str, Any], user_id: uuid.UUID):
        like = self.like_table(**create_dict)
        like.owner_id = user_id
        self.session.add(like)
        await self.session.commit()
        return like

    async def update(self, like: Like, status: bool):
        like.status = status
        await self.session.commit()

    async def get(self, user_id: uuid.UUID, video_id: uuid.UUID):
        statement = select(self.like_table).filter(
            self.like_table.owner_id == user_id, self.like_table.video_id == video_id)
        return await self._get(statement)

    async def _get(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def remove(self, user_id: uuid.UUID, video_id: uuid.UUID):
        statement = delete(self.like_table).where(
            self.like_table.owner_id == user_id, self.like_table.video_id == video_id)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()

    async def get_liked_users(self, video: Video):
        liked_users = await self.session.scalars(video.liked_users)
        return liked_users.all()

    async def get_disliked_users(self, video: Video):
        disliked_users = await self.session.scalars(video.disliked_users)
        return disliked_users.all()
