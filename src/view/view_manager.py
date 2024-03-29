import time
import uuid
from datetime import timedelta, datetime

from fingerprint_pro_server_api_sdk import Response
from fingerprint_pro_server_api_sdk.rest import ApiException

from src.user.models import User
from src.video.models import Video
from src.view.exceptions import ViewRecordException, LimitViewException, InvalidView, NonExistentView
from src.view.fingerprint import fingerprint_instance
from src.view.shemas import BaseView, ViewRead
from src.view.user_view_database_adapter import UserViewDatabaseAdapter
from src.view.view_database_adapter import ViewDatabaseAdapter


class ViewManager:
    max_views_per_day = 5

    def __init__(self,
                 view_db: ViewDatabaseAdapter,
                 user_view_db: UserViewDatabaseAdapter):
        self.view_db = view_db
        self.user_view_db = user_view_db

    async def record_view(self,
                          user: User,
                          view: BaseView,
                          video: Video) -> None:
        self._validate(view, video)
        if view.fingerprint and not self._validate_fingerprint(view.fingerprint):
            raise ViewRecordException
        if await self.count_viewer_video_views(user, view) >= self.max_views_per_day:
            view.viewing_time = None
        view = await self.view_db.create(view.dict(), user.id)
        if view.owner_id:
            user_view = await self.user_view_db.get(view.video_id, view.owner_id)
            if user_view:
                await self.user_view_db.update(user_view, view.id)
            else:
                user_view = ViewRead.from_orm(view).create_user_view_dict()
                user_view["view_id"] = view.id
                await self.user_view_db.create(user_view)

    async def remove_user_view(self,
                               user: User,
                               video_id: uuid.UUID
                               ) -> None:
        view = await self.user_view_db.get(video_id, user.id)
        if not view:
            raise NonExistentView
        await self.user_view_db.remove(video_id, user.id)

    async def get_viewed_users(self, video: Video):
        return await self.user_view_db.get_viewed_users(video)

    async def get_video_views(self, video: Video):
        return await self.view_db.get_video_views(video)

    async def count_video_views(self, video: Video):
        return len(await self.get_video_views(video))

    async def get_user_view(self, user: User, video: Video, ):
        user_view = await self.user_view_db.get(video.id, user.id)
        view = await self.view_db.get(user_view) if user_view else user_view
        return view

    async def count_viewer_video_views(self, user: User, view: BaseView):
        if user.id:
            return len(await self.view_db.get_user_video_views(user, view.video_id))
        else:
            return len(await self.view_db.get_viewer_video_views(view.fingerprint, view.video_id))

    def _validate(self,
                  view: BaseView,
                  video: Video
                  ) -> None:
        if view.viewing_time < timedelta(seconds=0):
            raise InvalidView(data={'reason': 'Viewed time cannot be negative'})
        elif view.stop_timecode < timedelta(seconds=0):
            raise InvalidView(data={'reason': 'Stoptimecode cannot be negative'})
        elif view.stop_timecode > video.duration:
            view.stop_timecode = video.duration
            # raise InvalidView(data={'reason': 'Stoptimecode cannot be more than the duration of the video'})
        elif view.viewing_time > video.duration:
            view.viewing_time = video.duration
            # raise InvalidView(data={'reason': 'Viewed time cannot be more than the duration of the video'})

    def _validate_fingerprint(self, fingerprint: str):
        try:
            visitor_visits: Response = fingerprint_instance.get_visits(fingerprint)
        except ApiException:
            raise ViewRecordException
        if not visitor_visits.visits:
            raise ViewRecordException
        visit_time = visitor_visits.visits[0].timestamp
        time_now = time.mktime(datetime.now().timetuple()) * 1000
        time_collision = time.mktime((datetime.now() - timedelta(hours=3)).timetuple()) * 1000
        return time_now > visit_time > time_collision or visitor_visits.visits[0].confidence.score > 0.94
