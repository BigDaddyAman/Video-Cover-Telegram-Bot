import asyncio
import logging
import random

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter

from redis_client.queue import (
    acknowledge_job,
    get_next_job,
)
from utils.telegram import restore_caption_entities


logger = logging.getLogger(__name__)


async def send_video_with_retry(bot: Bot, job: dict):
    entities = restore_caption_entities(
        job["caption_entities"]
    )

    while True:
        try:
            return await bot.send_video(
                chat_id=job["chat_id"],
                video=job["video_file_id"],
                cover=job["image_file_id"],
                caption=job["video_caption"],
                caption_entities=entities,
                supports_streaming=True,
                has_spoiler=job["has_spoiler"],
            )

        except TelegramRetryAfter as error:
            logger.warning(
                "Telegram flood limit reached. "
                "Waiting %s seconds.",
                error.retry_after,
            )

            await asyncio.sleep(
                error.retry_after
            )


async def process_job(bot: Bot, job: dict):
    user_id = job["user_id"]
    chat_id = job["chat_id"]

    try:
        await send_video_with_retry(
            bot,
            job,
        )

    except TelegramAPIError:
        logger.exception(
            "Failed to process video for user %s",
            user_id,
        )

        try:
            await bot.send_message(
                chat_id=chat_id,
                text=(
                    "❌ Sorry, I couldn't send the video "
                    "with that cover."
                ),
            )

        except TelegramAPIError:
            logger.exception(
                "Failed to send error message to user %s",
                user_id,
            )

        raise


async def worker(bot: Bot):
    logger.info("Background worker started.")

    while True:
        try:
            result = await get_next_job()

            if not result:
                continue

            message_id, job = result

            logger.info(
                "Processing job %s for user %s",
                message_id,
                job["user_id"],
            )

            await process_job(
                bot,
                job,
            )

            await acknowledge_job(
                message_id,
            )

            logger.info(
                "Job %s completed successfully.",
                message_id,
            )

            delay = random.uniform(2, 5)

            logger.info(
                "Waiting %.2f seconds before next video.",
                delay,
            )

            await asyncio.sleep(delay)

        except asyncio.CancelledError:
            logger.info("Worker stopped.")
            raise

        except Exception:
            logger.exception(
                "Unexpected worker error."
            )

            await asyncio.sleep(2)