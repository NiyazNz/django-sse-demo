import asyncio
from typing import AsyncIterator

from django.conf import settings
from django.http.response import ServerSentEventsMessage
from redis.asyncio.client import PubSub, Redis

from sse.channels import ChannelsLayer


class RedisChannelsLayer(ChannelsLayer):
    def __init__(self, channel_name: str, url: str = None) -> None:
        super().__init__(channel_name)
        self._url = url or settings.REDIS_URL
        self._redis: Redis = None
        self._pubsub: PubSub = None
        self._channel_iterator: AsyncIterator = None

    def __repr__(self):
        return f"{type(self).__name__}({self._url}/{self.channel_name})"

    @property
    def connection(self) -> Redis:
        if not self._redis:
            self._redis = Redis.from_url(settings.REDIS_URL)
        return self._redis

    @property
    def pubsub(self) -> PubSub:
        if not self._pubsub:
            self._pubsub = self.connection.pubsub()
        return self._pubsub

    async def get_channel_iterator(self) -> AsyncIterator:
        if not self._channel_iterator:
            await self.pubsub.subscribe(self.channel_name)
            self._channel_iterator = (
                message['data']
                async for message in self.pubsub.listen()
                if message['type'] != 'subscribe'
            )
        return self._channel_iterator

    async def receive(self) -> ServerSentEventsMessage:
        channel_iterator = await self.get_channel_iterator()
        message = await channel_iterator.__anext__()
        return ServerSentEventsMessage(message)

    async def send(self, message):
        return await self.connection.publish(self.channel_name, message)

    async def close(self) -> None:
        async with asyncio.Lock():
            if self._redis:
                if self._pubsub:
                    await self._pubsub.unsubscribe(self.channel_name)
                await self._redis.close()
            self._channel_iterator = None
            self._pubsub = None
            self._redis = None
