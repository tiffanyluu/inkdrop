import asyncio
import logging
from asyncpg import create_pool
from exceptions import EmailTemporaryError, EmailError
from db import notifications_db
from config import get_settings
from clients import send_email
from itertools import groupby
from html import escape

logger = logging.getLogger(__name__)


async def send_email_digest():
    settings = get_settings()
    pool = await create_pool(dsn=str(settings.database_url))
    success = 0
    failure = 0

    try:
        async with pool.acquire() as conn:
            rows = await notifications_db.list_unemailed_notifications(conn)
        for user_row_id, notifications in groupby(rows, key=lambda r: r["user_row_id"]):
            notifications = list(notifications)

            html = f"<p>Hi {escape(notifications[0]['first_name'])}, here are your new chapters:</p><ul>"
            for notification in notifications:
                html += f"<li>{escape(notification['title_name'])}: Chapter {notification['chapter']}</li>"
            html += "</ul>"

            if len(notifications) == 1:
                subject = "You have 1 new chapter!"
            else:
                subject = f"You have {len(notifications)} new chapters!"

            try:
                await send_email(
                    to=notifications[0]["email"],
                    subject=subject,
                    html=html,
                )
                success += 1
                async with pool.acquire() as conn:
                    await notifications_db.set_notification_emailed(
                        conn,
                        [
                            notification["notification_row_id"]
                            for notification in notifications
                        ],
                    )

            except (EmailTemporaryError, EmailError) as e:
                logger.error(
                    "Failed to send email to %s: %s", notifications[0]["email"], e
                )
                failure += 1
            except Exception as e:
                logger.exception(
                    "Unexpected error emailing %s",
                    notifications[0]["email"],
                )
                failure += 1

        logger.info("emailed %s, failed %s", success, failure)

    finally:
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(send_email_digest())
