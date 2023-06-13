from fastapi import Depends
from src.database import get_async_db_session
from src.view.models import View, UserView
from src.view.user_view_database_adapter import UserViewDatabaseAdapter
from src.view.view_database_adapter import ViewDatabaseAdapter
from src.view.view_manager import ViewManager


async def get_view_db(db_session=Depends(get_async_db_session)):
    yield ViewDatabaseAdapter(db_session, View)


async def get_user_view_db(db_session=Depends(get_async_db_session)):
    yield UserViewDatabaseAdapter(db_session, UserView)


async def get_view_manager(view_db=Depends(get_view_db), user_view_db=Depends(get_user_view_db)):
    yield ViewManager(view_db, user_view_db)
