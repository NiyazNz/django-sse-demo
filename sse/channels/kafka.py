from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from django.conf import settings
from sse.channels import ChannelsLayer


class KafkaChannelsLayer(ChannelsLayer):
    def __init__(self, channel_name: str, group_id: str = None, url: str = None) -> None:
        super().__init__(channel_name)
        self._consumer = None
        self._producer = None
        self._url = url or settings.KAFKA_URL
        self._group_id = group_id
        self._channel = None

    async def _get_consumer(self):
        if not self._consumer:
            self._consumer = AIOKafkaConsumer(
                self.channel_name,
                bootstrap_servers=self._url,
                enable_auto_commit=True,  # Is True by default anyway
                auto_commit_interval_ms=300,
                auto_offset_reset="latest",  # TODO
                group_id=self._group_id
            )
            await self._consumer.start()
        return self._consumer

    async def _get_producer(self):
        if not self._producer:
            self._producer = AIOKafkaProducer(bootstrap_servers=self._url)
            await self._producer.start()
        return self._producer

    async def receive(self):
        consumer = await self._get_consumer()
        message = await consumer.getone()
        return message.value

    async def send(self, message):
        producer = await self._get_producer()
        return await producer.send_and_wait(self.channel_name, message.encode('utf-8'))

    async def close(self):
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        self._consumer = None
        self._producer = None
