import uuid
from typing import Type, Dict, Any

from sqlalchemy import delete, Delete, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.view.models import UserView
from src.view.shemas import ViewRemove


class UserViewDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            user_view_table: Type[UserView],
    ):
        self.session = session
        self.user_view_table = user_view_table

    async def get(self, video_id, user_id):
        statement = select(self.user_view_table).where(
            self.user_view_table.author_id == user_id and self.user_view_table.video_id == video_id)
        return await self._get(statement)

    async def _get(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def create(self, create_dict: Dict[str, Any]):
        user_view = self.user_view_table(**create_dict)
        self.session.add(user_view)
        await self.session.commit()
        return user_view

    async def update(self, user_view: UserView, view_id: uuid.UUID):
        user_view.view_id = view_id
        await self.session.commit()

    async def remove(self, view: ViewRemove, user_id: uuid.UUID):
        statement = delete(self.user_view_table).where(
            self.user_view_table.author_id == user_id and self.user_view_table.video_id == view.video_id)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()
