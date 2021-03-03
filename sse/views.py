import asyncio
import json
import uuid
from datetime import datetime

import aioredis

from django.conf import settings
from django.http import JsonResponse, ServerSentEventsResponse
from sse.channels.kafka import KafkaChannelsLayer
from sse.channels.redis import RedisChannelsLayer
from sse.channels.response import ChannelsSseResponse


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


async def time_ticker():
    await asyncio.sleep(3)
    return datetime.now().isoformat()


async def background_task_sse_view(request):
    """Stream messages from background task"""
    return ServerSentEventsResponse(time_ticker, last_event_id=request.headers.get('Last-Event-ID', 0))


async def simple_redis_sse_view(request):
    """Stream messages from redis channel"""
    redis = await aioredis.create_redis(settings.REDIS_URL)
    channel, *_ = await redis.subscribe('sse')

    response = ServerSentEventsResponse(channel.get_json, last_event_id=request.headers.get('Last-Event-ID', 0))
    response.add_resource_closer(redis.close)
    return response


# the same as simple_redis_sse_view
async def redis_sse_view(request):
    """Stream messages from redis channel"""
    return ChannelsSseResponse(RedisChannelsLayer('sse'), last_event_id=request.headers.get('Last-Event-ID', 0))


async def kafka_sse_view(request):
    """Stream messages from kafka topic"""
    return ChannelsSseResponse(
        KafkaChannelsLayer('sse', group_id=str(uuid.uuid4())),
        last_event_id=request.headers.get('Last-Event-ID', 0)
    )
