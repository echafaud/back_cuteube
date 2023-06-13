from fastapi import Depends

from src.comment.comment_database_adapter import CommentDatabaseAdapter
from src.comment.comment_manager import CommentManager
from src.comment.models import Comment
from src.database import get_async_db_session


async def get_comment_db(db_session=Depends(get_async_db_session)):
    yield CommentDatabaseAdapter(db_session, Comment)


async def get_comment_manager(comment_db=Depends(get_comment_db)):
    yield CommentManager(comment_db)
