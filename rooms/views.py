from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

# Create your views here.

class MakeRoom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pass