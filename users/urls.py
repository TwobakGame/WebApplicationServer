from django.urls import path
from .views import SigninView, MyTokenObtainPairView, LogoutView, ChangePwView, ProfileUpdateView, DeleteUserView, SaveScoreView, RankView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'user'

urlpatterns = [
    # 회원가입
    path('signup/', SigninView.as_view(), name='signup'),
    # 로그인
    path('signin/',  MyTokenObtainPairView.as_view(), name='signin'),
    # 토큰 재발급
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # 로그아웃
    path('logout/',  LogoutView.as_view(), name='logout'),
    # 비밀번호 변경
    path('changepw/', ChangePwView.as_view(), name='changepw'),
    # 회원정보 수정
    path('profileupdate/', ProfileUpdateView.as_view(), name='profileupdate'),
    # 회원 탈퇴
    path('deleteuser/', DeleteUserView.as_view(), name='deleteuser'),
    # 점수 등록
    path('savescore/', SaveScoreView.as_view(), name='savescore'),
    # 랭킹 조회
    path('rank/', RankView.as_view(), name='rank'),
    
]