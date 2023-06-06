import uuid

from src.comment.comment_database_adapter import CommentDatabaseAdapter
from src.comment.shemas import BaseComment, CommentRead, CommentEdit, CommentRemove
from src.like.shemas import BaseLike
from src.auth.models import User
from src.video.models import Video


class CommentManager:
    def __init__(self, comment_db: CommentDatabaseAdapter):
        self.comment_db = comment_db

    async def post(self, user: User, comment: BaseComment) -> CommentRead:
        return await self.comment_db.create(comment.dict(), user.id)

    async def edit(self, user: User, comment: CommentEdit) -> CommentRead:
        comment_model = await self.comment_db.get(comment.id)
        if comment_model and user.id == comment_model.author_id:
            return await self.comment_db.edit(comment_model, comment.text)

    async def remove(self, user: User, id: uuid.UUID):
        comment_model = await self.comment_db.get(id)
        if comment_model and user.id == comment_model.author_id:
            await self.comment_db.remove(comment_model)

    async def get_video_comments(self, video: Video):
        return await self.comment_db.get_video_comments(video)
