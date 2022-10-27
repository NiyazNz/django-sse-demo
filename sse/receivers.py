import asyncio
from datetime import datetime

interval = 3


async def time_ticker_coro():  # coroutine function
    await asyncio.sleep(interval)
    return datetime.now().isoformat()


async def infinite_time_ticker():  # AsyncGenerator
    while True:
        await asyncio.sleep(interval)
        yield datetime.now().isoformat()


async def finite_time_ticker():  # AsyncGenerator
    message_count = 5
    for i in range(message_count):
        await asyncio.sleep(interval)
        yield f'{i + 1}/{message_count}-{datetime.now().isoformat()}'
    # EventSource client will reestablish connection and start new SSE.
    # You should stop `EventSource` on client side by sending EOF.
    yield 'EOF'


class TimeTicker:
    async def receive(self):  # async method
        await asyncio.sleep(interval)
        return datetime.now().isoformat()


class TimeTickerAsyncIterator:  # AsyncIterator
    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(interval)
        return datetime.now().isoformat()


class TimeTickerAsyncIterable:  # AsyncIterable
    def __init__(self):
        self.it = TimeTickerAsyncIterator()

    def __aiter__(self):
        return self.it
