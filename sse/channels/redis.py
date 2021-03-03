import aioredis

from django.conf import settings
from sse.channels import ChannelsLayer


class RedisChannelsLayer(ChannelsLayer):
    def __init__(self, channel_name: str, url=None) -> None:
        super().__init__(channel_name)
        self._redis = None
        self._url = url or settings.REDIS_URL
        self._channel = None

    async def _get_connection(self):
        if not self._redis:
            self._redis = await aioredis.create_redis(self._url)
        return self._redis

    async def receive(self):
        conn = await self._get_connection()
        if not self._channel:
            self._channel, *_ = await conn.subscribe(self.channel_name)
        message = await self._channel.get_json()
        return message

    async def send(self, message):
        conn = await self._get_connection()
        return await conn.publish_json(self.channel_name, message)

    async def close(self):
        if self._redis:
            if self._channel:
                await self._redis.unsubscribe(self.channel_name)
            self._redis.close()
        self._redis = None
        self._channel = None
