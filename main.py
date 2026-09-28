import asyncio
import logging

from aiogram import Bot, Dispatcher

from background_task.worker import worker
from config import BOT_TOKEN
from database.db import init_db
from handlers.start import router as start_router
from handlers.video import router as video_router

from redis_client.client import close_redis
from redis_client.queue import init_queue


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


dp.include_router(start_router)
dp.include_router(video_router)


async def main():
    await init_db()
    await init_queue()

    logger.info("Starting bot and worker...")

    try:
        await asyncio.gather(
            dp.start_polling(bot),
            worker(bot),
        )

    finally:
        await bot.session.close()
        await close_redis()

        logger.info("Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")