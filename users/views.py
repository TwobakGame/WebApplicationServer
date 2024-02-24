from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .serializers import SignUpSerializer, ChangePasswordSerializer, ProfileUpdateSerializer, DeleteUserSerializer, SaveScoreSerializer

from .models import RefreshToken, User, Rank

from django.utils import timezone

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# 스웨거 헤더 토큰
parameter_token = openapi.Parameter(
        "Authorization",
        openapi.IN_HEADER,
        description = "Bearer access_token",
        type = openapi.TYPE_STRING
    )


# 회원가입
class SigninView(APIView):
    @swagger_auto_schema(
    operation_id='회원가입',
    operation_description='회원가입',
    request_body=SignUpSerializer,
    responses={201: openapi.Response(
        description="201 CREATED",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="회원가입 성공"),
            }
        )
    )}
)
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'resultcode': 'SUCCESS','detail': '회원가입 성공'}, status=status.HTTP_201_CREATED)
        
        return Response({'resultcode':'FAIL','detail': serializer.errors},status= status.HTTP_400_BAD_REQUEST)
    

# 로그인 성공시 토큰 발급
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['userid'] = user.userid 
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        refresh_token, _ = RefreshToken.objects.get_or_create(user=self.user)
        refresh_token.token = str(refresh)
        refresh_token.save()
        return {'resultcode': 'SUCCESS', 'nickname': self.user.nickname, 'RefreshToken': data['refresh'],'AccessToken': data['access']}


# 로그인
class MyTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
    operation_id='로그인',
    operation_description='로그인',
    request_body=MyTokenObtainPairSerializer,
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'RefreshToken': openapi.Schema(type=openapi.TYPE_STRING),
                'AccessToken': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )}
)
    def post(self, request):
        serializer = MyTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'resultcode': 'FAIL', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

# 로그아웃
class LogoutView(APIView):
    permissions_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
    operation_id='로그아웃',
    operation_description='로그아웃',
    manual_parameters = [parameter_token],
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'detail': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )}
)
    def post(self, request):
        request.user.refresh_token.delete()

        return Response({'resultcode': 'SUCCESS', 'detail': '로그아웃 성공'}, status=status.HTTP_200_OK)
    

# 비밀번호 변경
class ChangePwView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
    operation_id='비밀번호 변경',
    operation_description='비밀번호 변경',
    manual_parameters = [parameter_token],
    request_body=ChangePasswordSerializer,
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'detail': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )}
)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            current_password = serializer.validated_data.get('current_password')
            new_password = serializer.validated_data.get('new_password')

            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return Response({'resultcode': 'SUCCESS', 'detail': '비밀번호 변경 성공'},status=status.HTTP_200_OK)
            else:
                return Response({
                    'resultcode': 'FAIL',
                    'detail': '현재 암호가 틀립니다.'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
                        'resultcode': 'FAIL',
                        'detail': serializer.details['new_password']
                        }, 
                        status=status.HTTP_400_BAD_REQUEST)
    

# 회원 정보 수정
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
    operation_id='회원정보 받기',
    operation_description='회원정보 받기',
    manual_parameters = [parameter_token],
    responses={200: openapi.Response(
        description="200 OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                'data' : openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'nickname': openapi.Schema(type=openapi.TYPE_STRING)
        })
            }
        )
    )}
)
    def get(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user)
        
        return Response({'resultcode': 'SUCCESS', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_id='회원정보 수정',
        operation_description='회원정보 수정',
        manual_parameters = [parameter_token],
        request_body=ProfileUpdateSerializer,
        responses={200: openapi.Response(
            description="200 OK",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'data' : openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING)
            })
                }
            )
        )}
    )
    def post(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'resultcode': 'SUCCESS', 'data': serializer.data}, status=status.HTTP_200_OK)
        
        return Response({
            'resultcode': 'FAIL',
            'detail': serializer.details
            }, 
            status=status.HTTP_400_BAD_REQUEST)


# 회원탈퇴
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='회원 탈퇴',
        operation_description='회원 탈퇴',
        manual_parameters = [parameter_token],
        request_body=ProfileUpdateSerializer,
        responses={200: openapi.Response(
            description="200 OK",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'detail': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )}
    )
    def post(self, request):
        user = request.user
        serializer = DeleteUserSerializer(data=request.data)

        if serializer.is_valid():
            password = serializer.validated_data.get('password')

            if user.check_password(password):
                try:
                    RefreshToken.objects.get(user_id=user.id).delete()
                    user.is_active = False
                    user.save()
                    return Response({'resultcode': 'SUCCESS','detail':'회원 탈퇴 성공'}, status=status.HTTP_200_OK)
                
                except RefreshToken.DoesNotExist:
                    return Response({
                        'resultcode': 'FAIL',
                        'detail': '유효하지 않는 유저정보 입니다.'
                        },
                        status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'resultcode': 'FAIL',
                'detail': '유효하지 않는 유저정보 입니다.'
                },
                status=status.HTTP_401_UNAUTHORIZED)
        

# 점수 등록
class SaveScoreView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_id='유저 점수 등록',
        operation_description='유저 점수 등록',
        manual_parameters = [parameter_token],
        request_body=SaveScoreSerializer,
        responses={200: openapi.Response(
            description="200 OK",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        "score": openapi.Schema(type=openapi.TYPE_STRING),
                        'score_time': openapi.Schema(type=openapi.TYPE_STRING)
                    })
                }
            )
        )}
    )
    def post(self, request):
        user_id = request.user.id
        current_time = timezone.now()
        formatted_time = current_time.strftime('%Y-%m-%d') 
        data = {'user':user_id, 'score': request.data.get('score', ''), 'score_time': formatted_time}
        serializer = SaveScoreSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            score_instance = serializer.save()
            return Response({'resultcode': 'SUCCESS', 'data': SaveScoreSerializer(score_instance).data}, status=status.HTTP_200_OK)
        
        return Response({
            'resultcode': 'FAIL',
            'detail': serializer.errors
            }, 
            status=status.HTTP_400_BAD_REQUEST)
    

# 랭킹
class RankView(APIView):
    @swagger_auto_schema(
        operation_id='랭킹',
        operation_description='랭킹',
        responses={200: openapi.Response(
            description="200 OK",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'resultcode': openapi.Schema(type=openapi.TYPE_STRING, description="SUCCESS"),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        "nickname":openapi.Schema(type=openapi.TYPE_STRING),
                        "score": openapi.Schema(type=openapi.TYPE_INTEGER),
                        'score_time': openapi.Schema(type=openapi.TYPE_STRING)
                    })
                }
            )
        )}
    )
    def get(self,request):
        data = Rank.objects.values('user__nickname','score','score_time').order_by('-score')[:10]

        return Response({'resultcode': 'SUCCESS', 'data':data}, status=status.HTTP_200_OK)