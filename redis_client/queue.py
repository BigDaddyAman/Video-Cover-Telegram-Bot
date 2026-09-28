from redis_client.client import redis_client
from redis_client.serializer import dumps, loads


STREAM_NAME = "video_cover:queue"
GROUP_NAME = "video_cover:workers"
CONSUMER_NAME = "worker-1"

CLAIM_IDLE_TIME = 300_000


async def init_queue():
    try:
        await redis_client.xgroup_create(
            STREAM_NAME,
            GROUP_NAME,
            id="0",
            mkstream=True,
        )
    except Exception as error:
        if "BUSYGROUP" not in str(error):
            raise


async def enqueue_job(job: dict):
    """Add a job to the Redis stream."""
    await redis_client.xadd(
        STREAM_NAME,
        {
            "data": dumps(job),
        },
    )


async def get_next_job():
    """Wait for a new job from the Redis stream."""

    result = await redis_client.xreadgroup(
        GROUP_NAME,
        CONSUMER_NAME,
        {
            STREAM_NAME: ">",
        },
        count=1,
        block=30_000,
    )

    if not result:
        return None

    _, messages = result[0]
    message_id, fields = messages[0]

    job = loads(fields[b"data"])

    return message_id, job


async def claim_stale_jobs():
    """Claim jobs abandoned by a crashed worker."""

    result = await redis_client.xautoclaim(
        STREAM_NAME,
        GROUP_NAME,
        CONSUMER_NAME,
        min_idle_time=CLAIM_IDLE_TIME,
        start_id="0-0",
        count=1,
    )

    messages = result[1]

    if not messages:
        return None

    message_id, fields = messages[0]

    job = loads(fields[b"data"])

    return message_id, job


async def acknowledge_job(message_id):
    """Mark a job as successfully processed."""
    await redis_client.xack(
        STREAM_NAME,
        GROUP_NAME,
        message_id,
    )
