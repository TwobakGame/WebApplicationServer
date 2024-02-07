from django.urls import path
from .views import MakeRoom, RoomSearch, RoomJoin

app_name = 'room'

urlpatterns = [
    # 방 생성
    path('make/', MakeRoom.as_view(), name='make'),
    # 방 조회
    path('inquiry/', MakeRoom.as_view(), name='inquiry'),
    # 모든 방 조회
    path('allinquiry/', RoomSearch.as_view(), name='allinquiry'),
    # 방 참여
    path('join/', RoomJoin.as_view, name='join'),
]