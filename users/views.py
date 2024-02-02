from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .serializers import SigninSerializer, ChangePasswordSerializer, ProfileUpdateSerializer, DeleteUserSerializer, SaveScoreSerializer

from .models import RefreshToken 

from django.utils import timezone


# 회원가입
class SigninView(APIView):
    def post(self, request):
        serializer = SigninSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '회원가입 성공'}, status=status.HTTP_201_CREATED)
        
        return Response({'error': serializer.errors,'error_code': status.HTTP_400_BAD_REQUEST},status= status.HTTP_400_BAD_REQUEST)
    

# 로그인 성공시 토큰 발급
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
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
        return {'RefreshToken': data['refresh'],'AccessToken': data['access']}


# 로그인
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# 로그아웃
class LogoutView(APIView):
    permissions_classes = [IsAuthenticated]

    def post(self, request):
        request.user.refresh_token.delete()

        return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)
    

# 비밀번호 변경
class ChangePwView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            current_password = serializer.validated_data.get('current_password')
            new_password = serializer.validated_data.get('new_password')

            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                return Response({'message': '비밀번호 변경 성공','status':200 },status=status.HTTP_200_OK)
            else:
                return Response({
                    'error_code': status.HTTP_400_BAD_REQUEST,
                    'error': '현재 암호가 틀립니다.'
                    },
                    status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
                        'error_code': status.HTTP_400_BAD_REQUEST,
                        'error': serializer.errors['new_password']
                        }, 
                        status=status.HTTP_400_BAD_REQUEST)
    

# 회원 정보 수정
class ProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({
            'error_code': status.HTTP_400_BAD_REQUEST,
            'error': serializer.errors
            }, 
            status=status.HTTP_400_BAD_REQUEST)


# 회원탈퇴
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

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
                    return Response({'message':'회원 탈퇴 성공','status':status.HTTP_200_OK}, status=status.HTTP_200_OK)
                except RefreshToken.DoesNotExist:
                    return Response({
                        'error_code': status.HTTP_404_NOT_FOUND,
                        'error': '유효하지 않는 유저정보 입니다.'
                        },
                        status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'error_code': status.HTTP_401_UNAUTHORIZED,
                'error': '유효하지 않는 유저정보 입니다.'
                },
                status=status.HTTP_401_UNAUTHORIZED)
        

# 점수 등록
class SaveScoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_time = timezone.now()
        formatted_time = current_time.strftime('%Y-%m-%d') 
        data = {'score': request.data.get('score', ''), 'score_time': formatted_time}
        serializer = SaveScoreSerializer(user, data=data, context={'request': request})

        if serializer.is_valid():
            score_instance = serializer.save()
            return Response(SaveScoreSerializer(score_instance).data, status=status.HTTP_200_OK)
        
        return Response({
            'error_code': status.HTTP_400_BAD_REQUEST,
            'error': serializer.errors
            }, 
            status=status.HTTP_400_BAD_REQUEST)