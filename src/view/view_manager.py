from datetime import timedelta

from src.auth.models import User
from src.view.shemas import BaseView, ViewRead, ViewRemove
from src.view.user_view_database_adapter import UserViewDatabaseAdapter
from src.view.view_database_adapter import ViewDatabaseAdapter


class ViewManager:
    def __init__(self, view_db: ViewDatabaseAdapter, user_view_db: UserViewDatabaseAdapter):
        self.view_db = view_db
        self.user_view_db = user_view_db

    async def record_view(self, user: User, view: BaseView):
        view = await self.view_db.create(view.dict(), user.id)
        if view.author_id:
            user_view = await self.user_view_db.get(view.video_id, view.author_id)
            if user_view:
                await self.user_view_db.update(user_view, view.id)
            else:
                user_view = ViewRead.from_orm(view).create_user_view_dict()
                user_view["view_id"] = user_view.pop("id")
                await self.user_view_db.create(user_view)

    async def remove_user_view(self, user: User, view: ViewRemove):
        await self.user_view_db.remove(view, user.id)
