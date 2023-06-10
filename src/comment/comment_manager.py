import uuid
from typing import List, Any

from src.comment.comment_database_adapter import CommentDatabaseAdapter
from src.comment.exceptions import InvalidComment, NonExistentComment
from src.comment.shemas import BaseComment, CommentRead, CommentEdit, CommentRemove
from src.like.shemas import BaseLike
from src.user.exceptions import AccessDenied
from src.user.models import User
from src.video.models import Video


class CommentManager:
    max_text_len = 5000
    min_text_len = 1

    def __init__(self,
                 comment_db: CommentDatabaseAdapter):
        self.comment_db = comment_db

    async def post(self,
                   user: User,
                   comment: BaseComment
                   ) -> CommentRead:
        self._validate(comment.text)
        return await self.comment_db.create(comment.dict(), user.id)

    async def edit(self,
                   user: User,
                   comment: CommentEdit
                   ) -> CommentRead:
        comment_model = await self.comment_db.get(comment.id)
        if not comment_model:
            raise NonExistentComment
        if user.id != comment_model.author_id:
            raise AccessDenied
        return await self.comment_db.edit(comment_model, comment.text)

    async def remove(self,
                     user: User,
                     id: uuid.UUID):
        comment_model = await self.comment_db.get(id)
        if not comment_model:
            raise NonExistentComment
        if user.id != comment_model.author_id:
            raise AccessDenied
        await self.comment_db.remove(comment_model)

    async def get_video_comments(self,
                                 video: Video,
                                 limit: int,
                                 pagination: int):
        comments = await self.comment_db.get_video_comments(video)
        return self._paginate(limit, pagination, comments)

    def _validate(self, text: str):
        if len(text) > self.max_text_len:
            raise InvalidComment(data={"reason": f'Maximum comment length is {self.max_text_len}'})
        if len(text) < self.min_text_len:
            raise InvalidComment(data={"reason": f'Minimum comment length is {self.min_text_len}'})

    def _paginate(self,
                  limit,
                  pagination,
                  result) -> List[Any]:
        return result[limit * pagination: limit * (pagination + 1)]
