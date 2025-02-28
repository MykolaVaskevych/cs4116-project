from rest_framework import serializers
from .models import Service, Booking

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id', 'title', 'description', 'price', 'provider',
            'category', 'location', 'is_remote', 'is_active',
            'featured', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'provider', 'status', 'created_at', 'updated_at']


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'id', 'service', 'customer', 'schedule_date', 'status',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']
