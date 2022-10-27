import json

from aiokafka import AIOKafkaConsumer
from redis.asyncio.client import Redis
from django.conf import settings
from django.http import JsonResponse, ServerSentEventsResponse

from sse import receivers
from sse.channels.kafka import KafkaChannelsLayer
from sse.channels.redis import RedisChannelsLayer
from sse.channels.response import ChannelsSseResponse

key = 'sse'


async def background_task_sse_view(request):
    """
    Example 1: Stream messages from background task

    Receiving messages from awaitable function. See also commented alternatives.
    """
    time_ticker = receivers.time_ticker_coro  # coroutine

    # Alternatively the following can be used as a message source:
    # time_ticker = receivers.infinite_time_ticker()  # AsyncGenerator
    # time_ticker = receivers.finite_time_ticker()  # AsyncGenerator
    # time_ticker = receivers.TimeTicker().receive  # async method
    # time_ticker = receivers.TimeTickerAsyncIterator()  # AsyncIterator
    # time_ticker = receivers.TimeTickerAsyncIterable()  # AsyncIterable

    return ServerSentEventsResponse(
        time_ticker,
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )


async def simple_redis_sse_view(request):
    """
    Example 2: Stream messages from redis channel

    Receiving messages from redis channel.
    """
    redis = Redis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    await pubsub.subscribe(key)
    channel_iterator = (
        message['data']
        async for message in pubsub.listen()
        if message['type'] != 'subscribe'
    )

    response = ServerSentEventsResponse(
        channel_iterator,
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )
    response.add_resource_closer(redis.close)
    return response


async def simple_kafka_sse_view(request):
    """
    Example 3: Stream messages from kafka topic

    Receiving messages from kafka topic.

    Alternatively `consumer.getone` can be used instead of iterator:
    ```
    async def get_one():
        message = await consumer.getone()
        return message.value

    response = ServerSentEventsResponse(
        get_one,  # <--
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )
    ```
    """
    consumer = AIOKafkaConsumer(
        key,
        bootstrap_servers=settings.KAFKA_URL,
        auto_commit_interval_ms=300,
        auto_offset_reset="latest",
    )
    await consumer.start()
    channel_iterator = (message.value async for message in consumer)
    response = ServerSentEventsResponse(
        channel_iterator,
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )
    response.add_resource_closer(consumer.stop)
    return response


async def redis_sse_view(request):
    """
    Example 4: Stream messages from redis channel

    Receiving messages from redis channel.

    Same as example 2 but delegates messages receiving and preprocessing to
    separate class implementing `receive` method - See `sse.channels.ChannelsLayer`.

    `ChannelsSseResponse` and `ChannelsLayer` should not be a part of PR to
    django code, and it is up to developer.
    """
    return ChannelsSseResponse(
        RedisChannelsLayer(key),
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )


async def kafka_sse_view(request):
    """
    Example 5: Stream messages from kafka topic

    Same as example 4 but uses kafka as a ChannelsLayer backend
    """
    return ChannelsSseResponse(
        KafkaChannelsLayer(key),
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )


async def send_view(request):
    """Send message to redis or kafka"""
    data = json.loads(request.body.decode("utf-8"))
    if data['broker'] == 'redis':
        publisher = RedisChannelsLayer(key)
    elif data['broker'] == 'kafka':
        publisher = KafkaChannelsLayer(key)
    else:
        return JsonResponse({'broker': 'invalid'}, status=400)

    await publisher.send(data['message'])
    await publisher.close()
    return JsonResponse({
        'status': f'Sent to {data["broker"]}'
    })
