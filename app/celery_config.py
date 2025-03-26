from celery import Celery

from config import settings

celery_app = Celery(
    main="lkeep",
    broker=str(settings.redis.url),
    backend=str(settings.redis.url),
)

celery_app.autodiscover_tasks(packages=[".app.mail"])
