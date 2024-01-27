from django.urls import path
from .views import MakeRoom

app_name = 'room'

urlpatterns = [
    # 방 생성
    path('make/', MakeRoom.as_view(), name='signin'),
]