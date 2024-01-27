from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import RoomSerializer

from django.core.cache import cache

import random

# Create your views here.

class MakeRoom(APIView):

    def generate_room_num(self):
        return random.randint(1, 9999)

    def post(self,request):
        room_name = request.data.get("roomName")
        room_num = self.generate_room_num()
        cache_key = f'room_{room_num}'
        
        if cache.get(cache_key) == None:
            cache.set(cache_key, {"roomNum": room_num, "roomName": room_name}, timeout=60*15)

            # serializer를 사용하지 않고 JSON 응답 생성
            response_data = {"roomNum": room_num, "roomName": room_name}

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response({'message': '다시 요청 바랍니다'})
