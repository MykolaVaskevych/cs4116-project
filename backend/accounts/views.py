# accounts/views.py
from rest_framework import status, permissions, viewsets, generics
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from .models import Wallet, Transaction, Service, Inquiry, InquiryMessage, Review
from .serializers import (
    UserSerializer, UserProfileSerializer, WalletSerializer,
    TransactionSerializer, DepositSerializer, WithdrawSerializer,
    TransferSerializer, ServiceSerializer, InquirySerializer,
    InquiryMessageSerializer, InquiryCreateSerializer, ReviewSerializer
)

User = get_user_model()


# Custom permissions
class IsBusinessUser(permissions.BasePermission):
    """
    Custom permission to only allow business users to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_business
        
    def has_object_permission(self, request, view, obj):
        # For create actions, has_permission is sufficient
        if request.method == 'POST':
            return True
            
        # For update/delete, check if the user owns the service
        if hasattr(obj, 'business'):
            return obj.business == request.user
            
        return False


class IsModeratorUser(permissions.BasePermission):
    """
    Custom permission to only allow moderator users to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class IsInquiryParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of an inquiry to view or interact with it.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Moderators can access any inquiry
        if user.is_moderator:
            return True
            
        # The customer who created the inquiry can access it
        if obj.customer == user:
            return True
            
        # The business user owning the service can access it
        if obj.service.business == user:
            return True
            
        return False


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user and return JWT tokens"""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Log in a user and return JWT tokens"""
    email = request.data.get('email', '')
    password = request.data.get('password', '')
    
    user = authenticate(email=email, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'role_display': user.get_role_display(),
                'is_business': user.is_business,
                'is_moderator': user.is_moderator
            }
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get or update the authenticated user's profile"""
    user = request.user
    
    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
        
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = UserProfileSerializer(user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def wallet_detail(request):
    """Get the authenticated user's wallet information"""
    wallet = request.user.wallet
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deposit(request):
    """Deposit funds to the user's wallet"""
    serializer = DepositSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        
        try:
            wallet = request.user.wallet
            transaction = wallet.deposit(amount)
            
            return Response({
                'message': f'Successfully deposited {amount}',
                'transaction_id': str(transaction.transaction_id),
                'new_balance': str(wallet.balance)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def withdraw(request):
    """Withdraw funds from the user's wallet"""
    serializer = WithdrawSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        
        try:
            wallet = request.user.wallet
            transaction = wallet.withdraw(amount)
            
            return Response({
                'message': f'Successfully withdrew {amount}',
                'transaction_id': str(transaction.transaction_id),
                'new_balance': str(wallet.balance)
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer(request):
    """Transfer funds to another user's wallet"""
    serializer = TransferSerializer(data=request.data)
    if serializer.is_valid():
        amount = serializer.validated_data['amount']
        recipient_email = serializer.validated_data['recipient_email']
        
        try:
            sender_wallet = request.user.wallet
            
            try:
                recipient = User.objects.get(email=recipient_email)
                recipient_wallet = recipient.wallet
            except User.DoesNotExist:
                return Response(
                    {'error': 'Recipient not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            transaction = sender_wallet.transfer(recipient_wallet, amount)
            
            return Response({
                'message': f'Successfully transferred {amount} to {recipient.email}',
                'transaction_id': str(transaction.transaction_id),
                'new_balance': str(sender_wallet.balance)
            })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def transaction_list(request):
    """List all transactions for the current user's wallet"""
    wallet = request.user.wallet
    transactions = Transaction.objects.filter(
        Q(from_wallet=wallet) | Q(to_wallet=wallet)
    ).order_by('-created_at')
    
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating services.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsBusinessUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Optionally restricts the returned services to those owned by the current business user.
        """
        queryset = Service.objects.all()
        
        # If a business user is viewing their services, filter the queryset
        if self.request.user.is_business and self.request.query_params.get('my_services', False):
            queryset = queryset.filter(business=self.request.user)
            
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Double-check that user is a business
        if not user.is_business:
            raise permissions.PermissionDenied("Only business users can create services")
            
        serializer.save(business=user)


class InquiryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and managing inquiries.
    """
    queryset = Inquiry.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InquiryCreateSerializer
        return InquirySerializer
    
    def get_queryset(self):
        """
        Filter inquiries based on user role:
        - Customers see their own inquiries
        - Businesses see inquiries related to their services
        - Moderators see all inquiries
        """
        user = self.request.user
        
        if user.is_moderator:
            return Inquiry.objects.all()
        
        if user.is_business:
            return Inquiry.objects.filter(service__business=user)
            
        # Regular customers
        return Inquiry.objects.filter(customer=user)
    
    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """
        Close an inquiry - only moderators can do this
        """
        inquiry = self.get_object()
        
        if not request.user.is_moderator:
            return Response(
                {'error': 'Only moderators can close inquiries'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        if inquiry.status == Inquiry.Status.CLOSED:
            return Response(
                {'error': 'Inquiry is already closed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        inquiry.close(request.user)
        serializer = self.get_serializer(inquiry)
        return Response(serializer.data)


class InquiryMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for creating and listing messages within an inquiry.
    """
    serializer_class = InquiryMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter messages to only show those from inquiries the user is a participant in
        Also allows filtering by inquiry ID
        """
        user = self.request.user
        
        # Base queryset based on user role
        if user.is_moderator:
            # Moderators can see all messages
            queryset = InquiryMessage.objects.all()
        elif user.is_business:
            # Businesses can see messages for inquiries related to their services
            queryset = InquiryMessage.objects.filter(inquiry__service__business=user)
        else:
            # Regular customers can only see their own inquiry messages
            queryset = InquiryMessage.objects.filter(inquiry__customer=user)
        
        # Filter by inquiry ID if provided in query params
        inquiry_id = self.request.query_params.get('inquiry', None)
        if inquiry_id:
            queryset = queryset.filter(inquiry__id=inquiry_id)
            
        return queryset
    
    def perform_create(self, serializer):
        inquiry = serializer.validated_data.get('inquiry')
        
        # Check if the user is a participant in this inquiry
        user = self.request.user
        
        if not (user.is_moderator or 
                inquiry.customer == user or 
                inquiry.service.business == user):
            raise permissions.PermissionDenied("You are not a participant in this inquiry")
            
        # Check if the inquiry is still open
        if inquiry.status != Inquiry.Status.OPEN:
            raise serializers.ValidationError("Cannot add messages to a closed inquiry")
            
        serializer.save(sender=user)
        
    def perform_update(self, serializer):
        # Check if the inquiry is still open before updating a message
        message = self.get_object()
        if message.inquiry.status != Inquiry.Status.OPEN:
            raise serializers.ValidationError("Cannot update messages in a closed inquiry")
        serializer.save()

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    View to list all reviews or create a new one.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle logic from the serializer's validation.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a review.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer