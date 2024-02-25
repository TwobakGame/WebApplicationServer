from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.cache import cache
from django_redis import get_redis_connection

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import random


# Create your views here.

class MakeRoom(APIView):

    def generate_room_num(self):
        return random.randint(1, 9999)

    @swagger_auto_schema(
        operation_id='방 조회',
        operation_description='방 조회',
        manual_parameters=[openapi.Parameter(
            'roomNum',
            openapi.IN_QUERY,
            description='방 번호',
            type=openapi.TYPE_STRING
        )],
        responses={200: openapi.Response(
            description="200 OK",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                                            properties={
                                                'roomName': openapi.Schema(type=openapi.TYPE_STRING),
                                                'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
                                                'roomPeople': openapi.Schema(type=openapi.TYPE_INTEGER)
                                            })
                }
            )
        )}
    )
    # 방 정보 가져오기
    def get(self,request):
        room_num = request.GET["roomNum"]
        cache_key = f'{room_num}'

        if cache.get(cache_key):
            request_data = cache.get(cache_key)
            return Response({'resultcode': 'SUCCESS', 'data': request_data}, status=status.HTTP_200_OK)
        
        return Response({'resultcode': 'FAIL', 'message': '존재하지 않는 방 코드 입니다.'},status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_id='방 만들기',
        operation_description='방 만들기',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'roomName': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={201: openapi.Response(
            description="201 CREATED",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                                            properties={
                                                'roomName': openapi.Schema(type=openapi.TYPE_STRING),
                                                'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
                                                'roomPeople': openapi.Schema(type=openapi.TYPE_INTEGER)
                                            })
                }
            )
        )}
    )
    # 방 만들기
    def post(self,request):
        room_name = request.data.get("roomName")
        room_num = self.generate_room_num()
        room_people = 1
        cache_key = f'{room_num}'
        
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
        data = []
        for key in all_keys:
            data.append(cache.get(int(key[3:])))

        for num, people in enumerate([i['roomPeople'] for i in data]):
            if people == 2:
                data.pop(num)
        

        return data
    
    @swagger_auto_schema(
    operation_id='전체 방 조회',
    operation_description='전체 방 조회',
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                                       properties={
                                            'roomName': openapi.Schema(type=openapi.TYPE_STRING),
                                            'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
                                            'roomPeople': openapi.Schema(type=openapi.TYPE_INTEGER)
                                       })
            }
        )
    )}
)
    def get(self,request):
        data = self.get_all_keys()

        return Response({'resultcode': 'SUCCESS', 'data': data}, status=status.HTTP_200_OK)
    

class RoomJoin(APIView):
    @swagger_auto_schema(
    operation_id='방 참여',
    operation_description='방 참여',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'data': openapi.Schema(type=openapi.TYPE_OBJECT,
                                       properties={
                                            'roomName': openapi.Schema(type=openapi.TYPE_STRING),
                                            'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
                                            'roomPeople': openapi.Schema(type=openapi.TYPE_INTEGER)
                                       })
            }
        )
    )}
)
    def post(self, request):
        room_num = request.data.get("roomNum")
        cache_key = f'{room_num}'
        room_info = cache.get(cache_key)

        if len(room_info) >= 1 | room_info['roomPeople'] < 2 :

            room_info['roomPeople'] += 1
            cache.set(cache_key, room_info, timeout=60*360)

            return Response({'resultcode': 'SUCCESS', 'data': cache.get(cache_key)}, status=status.HTTP_200_OK)

        return Response({'resultcode': 'FAIL', 'message': '일치하는 방 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
    

class RoomDelete(APIView):
    @swagger_auto_schema(
    operation_id='방 삭제',
    operation_description='방 삭제',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'roomNum': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'message': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
    )}
)
    # 방 삭제
    def post(self, request):
        room_num = request.data.get("roomNum")
        cache_key = f'{room_num}'

        if cache.get(cache_key):
            cache.delete(cache_key)

            return Response({'resultcode': 'SUCCESS', 'message': '방이 삭제되었습니다.'}, status=status.HTTP_200_OK)
            
        return Response({'resultcode': 'FAIL', 'message': '일치하는 방 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        