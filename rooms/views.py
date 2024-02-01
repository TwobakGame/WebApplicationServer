from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.core.cache import cache

import random

# Create your views here.

class MakeRoom(APIView):

    def generate_room_num(self):
        return random.randint(1, 9999)

    # 방 정보 가져오기
    def get(self,request):
        room_name = request.data.get("roomName")
        cache_key = f'room_{room_name}'

        if cache.get(cache_key):
            request_data = cache.get(cache_key)
            return Response(request_data, status=status.HTTP_200_OK)
        
        return Response({'message': '존재하지 않는 방 이름 입니다.'},status=status.HTTP_400_BAD_REQUEST)
    
    # 방 만들기
    def post(self,request):
        room_name = request.data.get("roomName")
        room_num = self.generate_room_num()
        room_people = 1
        cache_key = f'room_{room_name}'
        
        if cache.get(cache_key) == None:
            cache.set(cache_key, {"roomNum": room_num, "roomName": room_name, "room_people": room_people}, timeout=60*15)

            response_data = {"roomNum": room_num, "roomName": room_name, "room_people": room_people}

            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response({'message': '다시 요청 바랍니다'},status=status.HTTP_400_BAD_REQUEST)
