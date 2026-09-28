from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database.db import add_user


router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await add_user(message.from_user.id)

    await message.answer(
        "👋 Welcome!\n\n"
        "🎬 Send me a video, then send the image you'd like to use as its cover."
    )