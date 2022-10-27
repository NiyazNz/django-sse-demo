from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from sse import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('message/', ensure_csrf_cookie(TemplateView.as_view(template_name='message.html'))),
    path('send/', views.send_view),

    path('sse/', views.background_task_sse_view),
    # path('sse-redis/', views.simple_redis_sse_view),
    path('sse-redis/', views.redis_sse_view),
    # path('sse-kafka/', views.simple_kafka_sse_view),
    path('sse-kafka/', views.kafka_sse_view),
]
