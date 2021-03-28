import aioredis
from aioredis import Channel, Redis

from django.conf import settings
from django.http.response import ServerSentEventsMessage
from sse.channels import ChannelsLayer


class RedisChannelsLayer(ChannelsLayer):
    def __init__(self, channel_name: str, url: str = None) -> None:
        super().__init__(channel_name)
        self._redis: Redis = None
        self._url = url or settings.REDIS_URL
        self._channel: Channel = None

    async def _get_connection(self) -> Redis:
        if not self._redis:
            self._redis = await aioredis.create_redis(self._url)
        return self._redis

    async def _get_channel(self) -> Channel:
        conn = await self._get_connection()
        if not self._channel:
            self._channel, *_ = await conn.subscribe(self.channel_name)
        return self._channel

    async def receive(self) -> ServerSentEventsMessage:
        channel = await self._get_channel()
        message = await channel.get()
        return ServerSentEventsMessage(message)

    async def send(self, message):
        conn = await self._get_connection()
        return await conn.publish(self.channel_name, message)

    async def close(self) -> None:
        if self._redis:
            if self._channel:
                await self._redis.unsubscribe(self.channel_name)
            self._redis.close()
        self._redis = None
        self._channel = None
