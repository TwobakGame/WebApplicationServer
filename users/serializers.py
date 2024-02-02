from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


# 회원가입
class SigninSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['user_name', 'password', 'nickname']  
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    

# 비밀번호 변경
class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


# 회원 정보 수정
class ProfileUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['nickname']  


# 회원 탈퇴
class DeleteUserSerializer(serializers.Serializer):
     password = serializers.CharField(required=True, write_only=True)


# 점수 저장
class SaveScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['score', 'score_time']
