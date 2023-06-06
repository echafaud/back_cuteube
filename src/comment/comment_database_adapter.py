import uuid
from datetime import datetime
from typing import Type, Dict, Any

from sqlalchemy import select, Select, delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.comment.models import Comment
from src.comment.shemas import CommentEdit
from src.like.models import Like
from src.auth.models import User
from src.video.models import Video


class CommentDatabaseAdapter:
    def __init__(
            self,
            session: AsyncSession,
            comment_table: Type[Comment],
    ):
        self.session = session
        self.comment_table = comment_table

    async def create(self, create_dict: Dict[str, Any], user_id: uuid.UUID):
        comment = self.comment_table(**create_dict)
        comment.author_id = user_id
        self.session.add(comment)
        await self.session.commit()
        return comment

    async def edit(self, comment: Comment, edited_text: str):
        comment.text = edited_text
        comment.edited_at = datetime.utcnow()
        await self.session.commit()
        return comment

    async def get(self, id: uuid.UUID):
        statement = select(self.comment_table).where(self.comment_table.id == id)
        return await self._get_comment(statement)

    async def _get_comment(self, statement: Select):
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def remove(self, comment: Comment):
        statement = delete(self.comment_table).where(self.comment_table.id == comment.id)
        await self._remove(statement)

    async def _remove(self, statement: Delete):
        await self.session.execute(statement)
        await self.session.commit()

    async def get_video_comments(self, video: Video):
        comments = await self.session.scalars(video.comments)
        return comments.all()
