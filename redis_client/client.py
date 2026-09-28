import redis.asyncio as redis

from config import REDIS_URL
from redis_client.serializer import dumps, loads


redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=False,
    socket_connect_timeout=10,
    socket_timeout=None,
)


def user_key(user_id: int) -> str:
    return f"video_cover:user:{user_id}"


async def get_user(user_id: int):
    data = await redis_client.get(
        user_key(user_id)
    )

    if not data:
        return None

    return loads(data)


async def set_user(user_id: int, data: dict):
    await redis_client.set(
        user_key(user_id),
        dumps(data),
    )


async def delete_user(user_id: int):
    await redis_client.delete(
        user_key(user_id)
    )


async def push_waiting_video(
    user_id: int,
    video: dict,
) -> int:
    key = f"video_cover:waiting:{user_id}"

    length = await redis_client.rpush(
        key,
        dumps(video),
    )

    await redis_client.expire(
        key,
        3600,
    )

    return length


async def pop_all_waiting_videos(
    user_id: int,
) -> list[dict]:
    key = f"video_cover:waiting:{user_id}"

    async with redis_client.pipeline(transaction=True) as pipe:
        pipe.lrange(key, 0, -1)
        pipe.delete(key)

        result = await pipe.execute()

    videos = result[0]

    return [
        loads(video)
        for video in videos
    ]


async def close_redis():
    await redis_client.aclose()