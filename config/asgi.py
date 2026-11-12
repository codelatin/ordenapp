import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
from django.core.asgi import get_asgi_application
http_application = get_asgi_application()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from communications.routing import websocket_urlpatterns
application = ProtocolTypeRouter({
    'http': http_application,
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(websocket_urlpatterns))),
})
