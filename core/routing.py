# chat/routing.py
from django.urls import path

from . import consumers

websocket_urlpatterns = [
# want url to closely align with your views url
    #
    path('ws/group/<str:groupName>/', consumers.GroupConsumer),
    path('ws/chat/test/test_page/', consumers.TestConsumer),
    path('ws/feed/<str:feed>/', consumers.FeedConsumer),


]
