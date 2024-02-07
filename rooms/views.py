from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.core.cache import cache
from django_redis import get_redis_connection

import random

# Create your views here.

class MakeRoom(APIView):

    def generate_room_num(self):
        return random.randint(1, 9999)

    # 방 정보 가져오기
    def get(self,request):
        room_name = request.data.get("roomName")
        room_num = request.data.get("roomNum")
        cache_key = f'{room_num}_{room_name}'

        if cache.get(cache_key):
            request_data = cache.get(cache_key)
            return Response({'resultcode': 'SUCCESS', 'data': request_data}, status=status.HTTP_200_OK)
        
        return Response({'resultcode': 'FAIL', 'message': '존재하지 않는 방 코드 입니다.'},status=status.HTTP_400_BAD_REQUEST)
    
    # 방 만들기
    def post(self,request):
        room_name = request.data.get("roomName")
        room_num = self.generate_room_num()
        room_people = 1
        cache_key = f'{room_num}_{room_name}'
        
        if cache.get(cache_key) == None:
            cache.set(cache_key, {"roomNum": room_num, "roomName": room_name, "roomPeople": room_people}, timeout=60*360)

            response_data = {"roomNum": room_num, "roomName": room_name, "roomPeople": room_people}

            return Response({'resultcode': 'SUCCESS', 'data': response_data}, status=status.HTTP_201_CREATED)
        
        return Response({'resultcode': 'FAIL', 'message': '다시 요청 바랍니다'}, status=status.HTTP_400_BAD_REQUEST)
    

class RoomSearch(APIView):
    # 전체 방 조회
    def get_all_keys(self):
        redis_conn = get_redis_connection("default")

        all_keys = redis_conn.keys("*")

        return all_keys
    
    def get(self,request):
        data = self.get_all_keys()
        return Response({'resultcode': 'SUCCESS', 'data': data}, status=status.HTTP_200_OK)
    

class RoomJoin(APIView):
    def post(self, request):
        room_name = request.data.get("roomName")
        room_num = request.data.get("roomNum")
        cache_key = f'{room_num}_{room_name}'
        room_info = cache.get(cache_key)

        if room_info | room_info['roomPeople'] < 2 :

            room_info['roomPeople'] += 1
            cache.set(cache_key, room_info, timeout=60*360)

            return Response({'resultcode': 'SUCCESS', 'data': cache.get(cache_key)}, status=status.HTTP_200_OK)

        return Response({'resultcode': 'FAIL', 'message': '일치하는 방 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)