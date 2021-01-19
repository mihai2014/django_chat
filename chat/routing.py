from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    #re_path(r'ws/groups/',consumers.update_groups.as_asgi()),
    re_path(r'ws/data/',consumers.broadcast.as_asgi()),
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer),
    re_path(r'ws/chat/(?P<group_name>\w+)/(?P<user_name>.+)/$', consumers.ChatConsumer.as_asgi()),
]
