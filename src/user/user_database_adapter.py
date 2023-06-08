from typing import Optional, Dict, Any, Type
from uuid import UUID

from fastapi_users.models import UP
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.user.models import User


class UserDatabaseAdapter(SQLAlchemyUserDatabase):
    def __init__(
            self,
            session: AsyncSession,
            user_table: Type[User],
    ):
        self.session = session
        self.user_table = user_table

    async def create(self, create_dict: Dict[str, Any]) -> User:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await self.session.commit()
        return user

    async def get(self, id: UUID) -> Optional[User]:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_username(self, username: str) -> Optional[User]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> Optional[User]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def update(self, user: User, update_dict: Dict[str, Any]) -> User:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await self.session.commit()
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> Optional[User]:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()
