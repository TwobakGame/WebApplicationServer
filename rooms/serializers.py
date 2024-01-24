from rest_framework import serializers

from .models import room

class RoomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = room
        fields = '__all__'