from django.urls import path
from django.views.generic import TemplateView
from sse.views import (
    background_task_sse_view, kafka_sse_view, send_view, simple_redis_sse_view,
)

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('message', TemplateView.as_view(template_name='message.html')),
    path('send/', send_view),
    path('sse/', background_task_sse_view),
    path('sse-redis/', simple_redis_sse_view),
    path('sse-kafka/', kafka_sse_view),
]
