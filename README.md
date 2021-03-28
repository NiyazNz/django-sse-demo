# Django server sent events (SSE) demo

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

See [views.py](sse/views.py) for `ServerSentEventsResponse` usage examples.
