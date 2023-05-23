from src.like.like_database_adapter import LikeDatabaseAdapter
from src.like.shemas import BaseLike
from src.auth.models import User
from src.video.models import Video
from src.video.shemas import VideoView


class LikeManager:
    def __init__(self, like_db: LikeDatabaseAdapter):
        self.like_db = like_db

    async def rate(self, user: User, like: BaseLike):
        like_model = await self.like_db.get(user.id, like.video_id)
        if like_model and like_model.status != like.status:
            await self.like_db.update(like_model, like.status)
        elif not like_model:
            await self.like_db.create(like.dict(), user.id)

    async def remove_rating(self, user: User, like: BaseLike):
        like_model = await self.like_db.get(user.id, like.video_id)
        if like_model:
            await self.like_db.remove(user.id, like.video_id)
