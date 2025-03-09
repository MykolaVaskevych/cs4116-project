# accounts/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from .models import Wallet, Transaction
from .serializers import (
    UserSerializer, UserProfileSerializer, WalletSerializer, 
    TransactionSerializer, DepositSerializer, WithdrawSerializer, 
    TransferSerializer
)

User = get_user_model()


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
                'last_name': user.last_name
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