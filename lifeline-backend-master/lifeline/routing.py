from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.conf.urls import url
from lifeline.consumers import MessageConsumer


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(
            [url(r'^ws/messages/meta/(?P<jwt>[^/]+)/$', MessageConsumer)]
        )
    ),
})
