from aiogram import F, Router
from aiogram.types import Message

from redis_client.client import (
    pop_all_waiting_videos,
    push_waiting_video,
)
from redis_client.queue import enqueue_job
from utils.telegram import serialize_caption_entities


router = Router()


@router.message(F.video)
async def handle_video(message: Message):
    user_id = message.from_user.id
    video = message.video

    video_data = {
        "user_id": user_id,
        "chat_id": message.chat.id,
        "video_file_id": video.file_id,
        "video_caption": message.caption,
        "caption_entities": serialize_caption_entities(message),
        "has_spoiler": False,
    }

    queue_size = await push_waiting_video(
        user_id,
        video_data,
    )

    if queue_size == 1:
        await message.answer(
            "🎬 Videos received!\n\n"
            "🖼️ Send the cover image."
        )


@router.message(F.photo)
async def handle_photo(message: Message):
    user_id = message.from_user.id

    videos = await pop_all_waiting_videos(user_id)

    if not videos:
        await message.answer(
            "ℹ️ Please send some videos first, "
            "then send the cover image."
        )
        return

    largest = max(
        message.photo,
        key=lambda photo: photo.file_size or 0,
    )

    image_file_id = largest.file_id

    await message.answer(
        f"🖼️ Cover received!\n"
        f"⏳ {len(videos)} videos added to the queue."
    )

    for video in videos:
        job = {
            "user_id": video["user_id"],
            "chat_id": video["chat_id"],
            "video_file_id": video["video_file_id"],
            "image_file_id": image_file_id,
            "video_caption": video["video_caption"],
            "caption_entities": video["caption_entities"],
            "has_spoiler": video["has_spoiler"],
        }

        await enqueue_job(job)