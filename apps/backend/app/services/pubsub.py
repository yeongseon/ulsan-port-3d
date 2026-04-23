import json
from collections.abc import AsyncIterator

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from app.core.config import settings

CHANNEL_NAME = "ulsan-port-events"


class RedisPubSubService:
    def __init__(self) -> None:
        self._client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def publish(self, event_type: str, payload: dict[str, object]) -> None:
        message = json.dumps({"event": event_type, "payload": payload})
        await self._client.publish(CHANNEL_NAME, message)

    async def subscribe(self) -> PubSub:
        pubsub = self._client.pubsub()
        await pubsub.subscribe(CHANNEL_NAME)
        return pubsub

    async def iter_messages(self, pubsub: PubSub) -> AsyncIterator[dict[str, object]]:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                data = message.get("data")
                if isinstance(data, str):
                    yield json.loads(data)

    async def close_pubsub(self, pubsub: PubSub) -> None:
        await pubsub.unsubscribe(CHANNEL_NAME)
        await pubsub.close()
