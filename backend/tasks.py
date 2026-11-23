import asyncio
from scripts import sync_all_chapters, send_email_digest
from celery_app import app


@app.task
def email_digest():
    asyncio.run(send_email_digest())


@app.task
def scheduled_chapter_sync(send_email: bool = False):
    asyncio.run(sync_all_chapters())
    if send_email:
        email_digest.delay()
