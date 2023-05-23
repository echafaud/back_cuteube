from fastapi import Depends

from src.like.like_database_adapter import LikeDatabaseAdapter
from src.like.like_manager import LikeManager
from src.like.models import Like
from src.database import get_async_session


async def get_like_db(db_session=Depends(get_async_session)):
    yield LikeDatabaseAdapter(db_session, Like)


async def get_like_manager(like_db=Depends(get_like_db)):
    yield LikeManager(like_db)
