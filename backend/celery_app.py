from celery import Celery
from celery.schedules import crontab
from config import get_settings

settings = get_settings()
app = Celery("inkdrop", broker=str(settings.redis_url), include=["tasks"])

app.conf.update(
    enable_utc=True,
    timezone="America/Los_Angeles",
    beat_schedule={
        "sync-chapters": {
            "task": "tasks.scheduled_chapter_sync",
            "schedule": crontab(hour="9, 21", minute=0),
        }
    },
)
