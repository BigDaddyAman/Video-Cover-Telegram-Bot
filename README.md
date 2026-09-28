# Telegram Video Cover Bot — Advanced Version

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.31.0-2CA5E0)](https://github.com/aiogram/aiogram)
[![Redis](https://img.shields.io/badge/Redis-Supported-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![aiosqlite](https://img.shields.io/badge/aiosqlite-0.22.1-003B57)](https://github.com/omnilib/aiosqlite)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Telegram bot that lets users send videos and a cover image, then sends the videos back with the new cover applied.

## 🚂 Deploy on Railway

Deploy the bot to Railway with one click.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/video-cover-telegram-bot?referralCode=nIQTyp&utm_medium=integration&utm_source=template&utm_campaign=generic)

The Railway template sets up the required services and dependencies automatically.

After deployment, you only need to configure your bot token and any required environment variables.

The current architecture uses a single Telegram polling instance.

This is the **advanced / queue-based version** of the project. It is intended for larger self-hosted setups and production use.

> **Simple version:** The original lightweight version is available separately. It is easier to set up and understand, while this version adds Redis, background processing, batching, and a more reliable queue.

## ✨ What It Does

Users can send multiple videos and then send **one cover image** for the whole batch.

Example:

```text
Video 1
Video 2
Video 3
...
Video 10
        ↓
One cover image
        ↓
10 queue jobs
        ↓
Video 1 → send
          wait 2–5 sec
Video 2 → send
          wait 2–5 sec
...
Video 10 → send
```

The same cover is used for every video in the batch.

The worker also handles Telegram `RetryAfter` responses and waits for the amount of time requested by Telegram.

## 🚀 Why the Advanced Version?

The simple version processes a video as soon as it receives the cover. That works well for learning, testing, personal use, and small deployments.

The advanced version separates incoming work from outgoing work:

```text
Telegram
   ↓
Bot handlers
   ↓
Redis
   ↓
Redis Stream
   ↓
Background worker
   ↓
Telegram
```

This allows incoming batches to be queued instead of sending every video directly from the Telegram update handler.

### Comparison

| Feature | Simple Version | Advanced Version |
|---|---:|---:|
| Change video cover | ✅ | ✅ |
| Preserve captions | ✅ | ✅ |
| SQLite | ✅ | ✅ |
| Redis | ❌ | ✅ |
| Background worker | ❌ | ✅ |
| Redis Stream queue | ❌ | ✅ |
| Multiple videos per batch | ❌ | ✅ |
| One cover for multiple videos | ❌ | ✅ |
| Delayed video delivery | ❌ | ✅ |
| Telegram `RetryAfter` handling | Basic | ✅ |
| Queue acknowledgement | ❌ | ✅ |
| Stale-job recovery | ❌ | ✅ |

## 🖼️ Batch Workflow

The basic workflow is:

1. Send multiple videos.
2. The bot acknowledges the batch without replying to every video.
3. Send one cover image.
4. The bot creates one queue job for each video.
5. A background worker sends the videos gradually.

For example:

```text
User:
  Video 1
  Video 2
  Video 3
  Video 4

Bot:
  🎬 Videos received!
  🖼️ Send the cover image.

User:
  Cover image

Bot:
  🖼️ Cover received!
  ⏳ 4 videos added to the queue.
```

Then the worker sends all four videos one by one.

## 🧱 Architecture

### Redis Waiting Queue

Each user's waiting videos are kept in a separate queue:

```text
video_cover:waiting:<user_id>

    Video 1
    Video 2
    Video 3
    Video 4
```

When the cover arrives, the waiting videos are collected and turned into individual jobs.

### Redis Stream

Each video is added as its own queue job:

```text
Job 1 → Video 1 + cover
Job 2 → Video 2 + cover
Job 3 → Video 3 + cover
Job 4 → Video 4 + cover
```

The worker only acknowledges a job after it has been processed successfully.

### Background Worker

The worker does the following:

1. Gets the next job.
2. Sends the video.
3. Acknowledges the Redis Stream job.
4. Waits 2–5 seconds.
5. Processes the next job.

If Telegram responds with `RetryAfter`, the worker waits for the requested time and then tries again.

## 🛡️ Queue Reliability

This version uses Redis Streams instead of a basic Redis list.

The flow looks like this:

```text
New job
   ↓
Redis Stream
   ↓
Worker receives job
   ↓
Process successfully
   ↓
XACK
```

The project also uses `XAUTOCLAIM` to recover jobs that are left pending if a worker stops or fails.

This is more reliable than removing a job from a basic queue as soon as a worker receives it.

## ⏱️ Sending Delay

The worker currently waits for a random amount of time between successful sends:

```python
delay = random.uniform(2, 5)
await asyncio.sleep(delay)
```

The delay is kept fairly conservative:

```text
2.0s
2.8s
3.7s
4.9s
...
```

This helps avoid sending a large number of videos in a short burst.

This **does not guarantee that Telegram flood limits will never happen**. Telegram can still return `RetryAfter`, so the retry handling is still enabled.

## 👥 Multiple Users

The current setup uses one background worker:

```text
User A ─┐
User B ─┤
User C ─┼──→ Redis Stream ──→ Worker ──→ Telegram
User D ─┤
User E ─┘
```

This keeps outgoing video delivery controlled.

Multiple workers can be added later with proper per-user and global rate limiting. Increasing the worker count without rate limiting is not recommended because multiple workers could send videos at the same time.

## 📁 Project Structure

```text
Video-Cover-Telegram-Bot/
│
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.txt
├── config.py
├── main.py
│
├── background_task/
│   ├── __init__.py
│   └── worker.py
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   └── video.py
│
├── redis_client/
│   ├── __init__.py
│   ├── client.py
│   ├── queue.py
│   └── serializer.py
│
└── utils/
    ├── __init__.py
    └── telegram.py
```

## ⚙️ Requirements

- Python 3.13
- aiogram
- Redis
- orjson
- python-dotenv
- aiosqlite
- zstandard

Use the package versions listed in `requirements.txt`.

## 📦 Why These Dependencies?

The advanced version includes a few dependencies that support the current architecture and leave room for future improvements.

- **aiogram** — Handles Telegram bot updates, messages, and API requests.

- **Redis** — Stores temporary video batches and manages the background job queue.

- **aiosqlite** — Stores persistent Telegram user IDs for future features such as broadcasts, user management, and statistics.

- **orjson** — Provides fast JSON serialization and deserialization for queue/job data.

- **zstandard** — Provides fast compression and can be useful as queue data or stored job payloads become larger.

- **python-dotenv** — Loads configuration and secrets from the `.env` file.

Some dependencies are included with future upgrades in mind, so the project can evolve without changing the basic architecture later.

## 🔐 Environment Variables

Example:

```env
BOT_TOKEN=your_bot_token_here
REDIS_URL=redis://localhost:6379/0
```

Do not commit your real `.env` file or bot token to the repository.

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/BigDaddyAman/Video-Cover-Telegram-Bot.git
cd Video-Cover-Telegram-Bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Redis

Make sure Redis is running locally, or use a hosted Redis instance.

For local Redis:

```bash
redis-server
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Then configure:

```env
BOT_TOKEN=your_bot_token_here
REDIS_URL=redis://localhost:6379/0
```

### 5. Start the bot

```bash
python main.py
```

You should see logs similar to:

```text
Starting bot and worker...
Start polling
Background worker started.
```

## 🐳 Docker

Build:

```bash
docker build -t video-cover-bot .
```

Run:

```bash
docker run -d   --name video-cover-bot   --env-file .env   video-cover-bot
```

View logs:

```bash
docker logs -f video-cover-bot
```

## 🧪 Testing

For a basic test, send:

```text
Video 1
Video 2
Video 3
Video 4
Video 5
```

Then send one cover image.

Expected:

```text
🖼️ Cover received!
⏳ 5 videos added to the queue.
```

The bot should then send the five videos one by one with a delay between them.

The original captions and their formatting should stay unchanged.

## 🔄 Simple vs Advanced

Both versions are useful for different setups.

### Simple version

The simple version is suitable for:

- Minimal setup
- No Redis
- Easy learning
- Personal use
- Small self-hosted deployments
- A small codebase that is easy to understand

### Advanced version

The advanced version is suitable for:

- Multiple videos per batch
- One cover applied to many videos
- Background processing
- Redis-backed queues
- Better handling of bursts of incoming work
- Controlled outgoing delivery
- Queue acknowledgement
- Recovery of abandoned queue jobs
- A foundation for future scaling

The advanced version has more components, so it is naturally more complex.

## 🛣️ Future Improvements

Some possible improvements for later:

- Configurable worker count
- Unique Redis consumer per worker
- Per-user rate limiting
- Global Telegram rate limiting
- Queue progress messages
- `/cancel` command
- Better queue monitoring
- Metrics and health monitoring
- Improved retry policies
- Job prioritization

These can be added separately without changing how the current system works.

## 🔒 Security Notes

Never commit:

```text
.env
bot tokens
Redis passwords
private deployment credentials
sensitive database files
```

Keep secrets in environment variables.

## 📄 License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.
