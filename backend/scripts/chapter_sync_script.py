import asyncio
import logging
from asyncpg import create_pool
from exceptions import MangadexError, MangadexNotFoundError
from controllers import titles_controller
from db import titles_db
from config import get_settings
from clients import MangadexClient

logger = logging.getLogger(__name__)


async def sync_all_chapters():
    settings = get_settings()
    pool = await create_pool(dsn=str(settings.database_url))
    mangadex_client = MangadexClient()
    success = 0
    failure = 0

    try:
        async with pool.acquire() as conn:
            rows = await titles_db.list_sources_with_subscribers(conn)
        for row in rows:
            try:
                await titles_controller.sync_chapters(
                    pool, mangadex_client, row["source_id"], row["source_type"]
                )
                success += 1
            except (MangadexError, MangadexNotFoundError) as e:
                logger.error(
                    "Failed to sync %s source %s: %s",
                    row["source_type"],
                    row["source_id"],
                    e,
                )
                failure += 1
            except Exception:
                logger.exception(
                    "Unexpected error syncing %s source %s",
                    row["source_type"],
                    row["source_id"],
                )
                failure += 1
        logger.info("synced %s, failed %s", success, failure)
    finally:
        await mangadex_client.close()
        await pool.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(sync_all_chapters())
