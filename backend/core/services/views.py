from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Service, Booking
from .serializers import ServiceSerializer, BookingSerializer
from accounts.models import User

class CreateServiceView(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        # Only providers can create services
        if not user.can_sell:
            raise PermissionDenied("You must be a provider to create services.")
        
        serializer.save(provider=user, status='pending', is_active=False)


class ApproveServiceView(generics.UpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not request.user.is_moderator:
            return Response({'detail': 'Only moderators can approve services.'},
                            status=status.HTTP_403_FORBIDDEN)
        
        service = self.get_object()
        if service.status != 'pending':
            return Response({'detail': 'Service is not in pending status.'},
                            status=status.HTTP_400_BAD_REQUEST)
        
        service.status = 'approved'
        service.is_active = True
        service.save()
        return Response({'detail': f'Service "{service.title}" approved.'},
                        status=status.HTTP_200_OK)


class RejectServiceView(generics.UpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not request.user.is_moderator:
            return Response({'detail': 'Only moderators can reject services.'},
                            status=status.HTTP_403_FORBIDDEN)

        service = self.get_object()
        if service.status != 'pending':
            return Response({'detail': 'Service is not in pending status.'},
                            status=status.HTTP_400_BAD_REQUEST)

        service.status = 'rejected'
        service.is_active = False
        service.save()
        return Response({'detail': f'Service "{service.title}" rejected.'},
                        status=status.HTTP_200_OK)


class CreateBookingView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        # Moderator cannot book. Also ensure 'can_buy'.
        if not user.can_buy:
            raise PermissionDenied("You cannot book services.")
        
        serializer.save(customer=user, status='pending')


class UpdateBookingStatusView(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        booking = self.get_object()
        user = request.user

        # If the booking's service belongs to 'provider', or user is 'moderator',
        # we allow them to update booking status. 
        if booking.service.provider != user and not user.is_moderator:
            return Response({'detail': 'Not allowed to update this booking.'},
                            status=status.HTTP_403_FORBIDDEN)

        new_status = request.data.get('status')
        if new_status not in ['confirmed', 'completed', 'cancelled']:
            return Response({'detail': 'Invalid status.'},
                            status=status.HTTP_400_BAD_REQUEST)

        booking.status = new_status
        booking.save()

        return Response({'detail': f'Booking status changed to {new_status}.'},
                        status=status.HTTP_200_OK)
