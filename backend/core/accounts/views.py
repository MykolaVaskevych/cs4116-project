from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework.generics import ListAPIView

from .serializers import (
    ChangePasswordSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer
)
from .models import User

class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
            
            user = authenticate(username=user.username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
        return Response(data)

    def put(self, request):
        """
        Update basic profile fields. 
        """
        user = request.user
        user.username = request.data.get('username', user.username)
        user.email = request.data.get('email', user.email)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save()
        return Response({"message": "Profile updated successfully."})


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            user = request.user
            # verify old password
            if not check_password(old_password, user.password):
                return Response({'detail': 'Old password does not match.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password updated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestBusinessAccountView(APIView):
    """
    Customer can request to become a provider. 
    We'll set role='pending_provider'. A separate Admin/Moderator view
    will finalize the approval.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role == 'provider':
            return Response({'detail': 'You are already a provider.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role == 'pending_provider':
            return Response({'detail': 'You have already requested provider status.'}, status=status.HTTP_400_BAD_REQUEST)
        if user.role == 'moderator':
            return Response({'detail': 'Moderators cannot become providers.'}, status=status.HTTP_400_BAD_REQUEST)

        user.role = 'pending_provider'
        user.save()
        return Response({'detail': 'Business account request submitted. Await moderator approval.'}, status=status.HTTP_200_OK)


class ApproveProviderView(APIView):
    """
    Moderator can approve user whose role = 'pending_provider' => 'provider'.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not request.user.is_moderator:
            return Response({'detail': 'Only moderators can approve providers.'}, status=status.HTTP_403_FORBIDDEN)
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if target_user.role != 'pending_provider':
            return Response({'detail': 'User is not in pending_provider status.'}, status=status.HTTP_400_BAD_REQUEST)

        target_user.role = 'provider'
        target_user.save()
        return Response({'detail': f'User {target_user.username} is now a provider.'}, status=status.HTTP_200_OK)


class ListPendingProvidersView(ListAPIView):
    """
    Returns a list of users where role='pending_provider'.
    Only accessible to moderators.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegistrationSerializer  # or a custom "UserListSerializer"

    def get_queryset(self):
        if not self.request.user.is_moderator:
            # Return empty or raise an exception
            return User.objects.none()
        return User.objects.filter(role='pending_provider')