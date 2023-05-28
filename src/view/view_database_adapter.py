import uuid
from datetime import timedelta
from typing import Type, Dict, Any, Optional

from sqlalchemy import select, Select, delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.view.models import View
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
        view.author_id = user_id
        if view.viewing_time < timedelta(seconds=15):
            view.viewing_time = None
        self.session.add(view)
        await self.session.commit()
        return view
