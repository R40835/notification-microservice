import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import OriginValidator

from notification.routing import websocket_urlpatterns
from notification.middleware import WebsocketAuthMiddleware

from django.conf import settings

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": OriginValidator(
            WebsocketAuthMiddleware(
                URLRouter(
                    websocket_urlpatterns
                )
            ),
            [settings.FRONTEND_ORIGIN],
        ),
    }
)