# Django server sent events (SSE) demo

Demo project for a django SSE feature implementation from 
[github.com/NiyazNz/django.git@serverSentEvent](https://github.com/NiyazNz/django/tree/serverSentEvents)
which extends `ASGIHandler` to handle async data streaming and adds 
`ServerSentEventsResponse`.

- [HTML Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events)
- [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)

## Examples

See [views.py](sse/views.py) for `ServerSentEventsResponse` usage examples.

## Usage

Install requirements

```
pip install -r requirements.txt
```

Start server:

```
uvicorn sse_demo.asgi:application
```

Open browser on http://localhost:8000. Open dev tools console/network tab to see
messages.

Open http://localhost:8000/message/ in a new tab to send messages.
