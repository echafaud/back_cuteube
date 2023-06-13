import celery

from src.config import REDIS_HOST, REDIS_PORT

CELERY_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

celery = celery.Celery('celery', broker=CELERY_URL)
celery.autodiscover_tasks(['src.user.tasks'])
