from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/notification/<user_id>/", consumers.NotificationConsumer.as_asgi()),
    path("ws/event/", consumers.EventConsumer.as_asgi()),
]
