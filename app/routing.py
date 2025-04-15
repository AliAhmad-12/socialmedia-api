from django.urls import path

from .consumers  import *

websocket_urlpatterns=[
path('ws/ac/<int:room_id>/',ChatConsumer.as_asgi(),)
]