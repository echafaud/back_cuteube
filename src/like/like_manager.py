import uuid

from src.like.like_database_adapter import LikeDatabaseAdapter
from src.like.shemas import BaseLike
from src.user.models import User
from src.video.models import Video
from src.video.shemas import VideoView


class LikeManager:
    def __init__(self, like_db: LikeDatabaseAdapter):
        self.like_db = like_db

    async def rate(self, user: User, like: BaseLike):
        like_model = await self.like_db.get(user.id, like.video_id)
        if like_model and like.status is None:
            await self.remove_rating(user, like.video_id)
        elif like_model and like_model.status != like.status:
            await self.like_db.update(like_model, like.status)
        elif not like_model:
            await self.like_db.create(like.dict(), user.id)

    async def remove_rating(self, user: User, video_id: uuid.UUID):
        like_model = await self.like_db.get(user.id, video_id)
        if like_model:
            await self.like_db.remove(user.id, video_id)

    async def get_rate(self, user: User, video: Video):
        return await self.like_db.get(user.id, video.id)

    async def get_liked_users(self, video: Video):
        return await self.like_db.get_liked_users(video)

    async def get_disliked_users(self, video: Video):
        return await self.like_db.get_disliked_users(video)

    async def count_video_likes(self, video: Video):
        return len(await self.get_liked_users(video))

    async def count_video_dislikes(self, video: Video):
        return len(await self.get_disliked_users(video))
