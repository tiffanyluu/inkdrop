import asyncio

from scripts import sync_all_chapters
from celery_app import app


@app.task
def scheduled_chapter_sync():
    asyncio.run(sync_all_chapters())
