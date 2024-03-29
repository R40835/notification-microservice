from rest_framework import serializers
from .models import AppNotification


class AppNotificationSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(read_only=True)
    text = serializers.CharField(read_only=True)

    class Meta:
        model = AppNotification
        fields = '__all__'