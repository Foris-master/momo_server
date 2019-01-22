# chat/routing.py
from django.urls import re_path

from .consumers import ModemConsumer

websocket_urlpatterns = [
    re_path(r'^ws/modem/(?P<tag>[^/]+)/$', ModemConsumer),
]