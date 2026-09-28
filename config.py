import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)


if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN is not set. Please add it to your .env file."
    )