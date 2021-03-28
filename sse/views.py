import asyncio
import json
from datetime import datetime

import aioredis

from django.conf import settings
from django.http import JsonResponse, ServerSentEventsResponse
from sse.channels.kafka import KafkaChannelsLayer
from sse.channels.redis import RedisChannelsLayer
from sse.channels.response import ChannelsSseResponse

interval = 3


async def send_view(request):
    data = json.loads(request.body.decode("utf-8"))
    if data['broker'] == 'redis':
        publisher = RedisChannelsLayer('sse')
    elif data['broker'] == 'kafka':
        publisher = KafkaChannelsLayer('sse')
    else:
        return JsonResponse({'broker': 'invalid'}, status=400)

    await publisher.send(data['message'])
    await publisher.close()
    return JsonResponse({
        'status': f'Sent to {data["broker"]}'
    })


async def time_ticker_coro():  # coroutine function
    await asyncio.sleep(interval)
    return datetime.now().isoformat()


async def infinite_time_ticker():  # AsyncGenerator
    while True:
        await asyncio.sleep(interval)
        yield datetime.now().isoformat()


async def finite_time_ticker():
    message_count = 5
    for i in range(message_count):
        await asyncio.sleep(interval)
        yield f'{i+1}/{message_count}-{datetime.now().isoformat()}'
    # EventSource client will reestablish connection and start new SSE.
    # You should stop EventSource on client side.
    yield 'EOF'


# Example 1
#   Receiving messages from awaitable function or AsyncGenerator
async def background_task_sse_view(request):
    """Stream messages from background task"""
    time_ticker = time_ticker_coro
    # Alternatively AsyncGenerators can be used as a message source:
    # time_ticker = infinite_time_ticker()
    # time_ticker = finite_time_ticker()

    return ServerSentEventsResponse(time_ticker, last_event_id=request.headers.get('Last-Event-ID', 0))


# Example 2
#   Receiving messages from redis channel
async def simple_redis_sse_view(request):
    """Stream messages from redis channel"""
    redis = await aioredis.create_redis(settings.REDIS_URL)
    channel, *_ = await redis.subscribe('sse')

    # `channel.get`, `channel.get_json` coroutine functions or `channel.iter()`
    # AsyncIterator can be used as a message source
    response = ServerSentEventsResponse(channel.get, last_event_id=request.headers.get('Last-Event-ID', 0))
    response.add_resource_closer(redis.close)
    return response


# Example 3
#   Receiving messages from redis channel.
#
#   Same as example 2 but delegates messages receiving and preprocessing to
#   separate class implementing `receive` method - See `sse.channels.ChannelsLayer`.
#   `ChannelsSseResponse` and `ChannelsLayer` should not be a part of MR and it
#   is up to developer.
async def redis_sse_view(request):
    """Stream messages from redis channel"""
    return ChannelsSseResponse(RedisChannelsLayer('sse'), last_event_id=request.headers.get('Last-Event-ID', 0))


# Example 4
#   Same as example 3 but uses kafka as a ChannelsLayer backend
async def kafka_sse_view(request):
    """Stream messages from kafka topic"""
    return ChannelsSseResponse(KafkaChannelsLayer('sse'), last_event_id=request.headers.get('Last-Event-ID', 0))
