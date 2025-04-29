# accounts/views.py
from rest_framework import status, permissions, viewsets, generics, filters, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Wallet, Transaction, Service, Inquiry, InquiryMessage, 
    Review, ReviewComment, Category, BlogCategory, BlogPost, BlogComment,
    PaymentRequest, User, Conversation, ConversationMessage, VerifiedServiceCustomer,
    SupportTicket, SupportMessage
)
from .serializers import (
    UserSerializer, UserProfileSerializer, WalletSerializer,
    TransactionSerializer, DepositSerializer, WithdrawSerializer,
    TransferSerializer, ServiceSerializer, InquirySerializer,
    InquiryMessageSerializer, InquiryCreateSerializer, 
    ReviewSerializer, ReviewCommentSerializer, CategorySerializer,
    BlogCategorySerializer, BlogPostListSerializer, BlogPostDetailSerializer,
    BlogPostCreateSerializer, BlogCommentSerializer, ModeratorSerializer,
    ModeratorRequestSerializer, PaymentRequestSerializer, PaymentRequestActionSerializer,
    ChangePasswordSerializer, ConversationSerializer, ConversationMessageSerializer,
    ConversationCreateSerializer, ConversationActionSerializer,
    SupportTicketSerializer, SupportMessageSerializer, SupportTicketCreateSerializer,
    SupportTicketCloseSerializer
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
        # Handle file uploads - no need for 'files' argument, DRF handles this automatically
        serializer = UserProfileSerializer(user, data=request.data, partial=partial)
            
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """
    Change password for the authenticated user.
    
    Requires old_password, new_password, and confirm_password.
    Validates that old password is correct, new passwords match,
    and the new password meets all security requirements.
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        # Set the new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {'message': 'Password updated successfully'},
            status=status.HTTP_200_OK
        )
    
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


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and managing service categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        - Create/Update/Delete: Only moderators 
        - List/Retrieve: Any authenticated user
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsModeratorUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating services.
    """
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']  # Default ordering
    
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
        Also supports filtering by category.
        """
        queryset = Service.objects.all()
        
        # If a business user is viewing their services, filter the queryset
        if self.request.user.is_business and self.request.query_params.get('my_services', False):
            queryset = queryset.filter(business=self.request.user)
            
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
    
    def perform_create(self, serializer):
        user = self.request.user
        
        # Double-check that user is a business
        if not user.is_business:
            raise permissions.PermissionDenied("Only business users can create services")
            
        serializer.save(business=user)
    
    @action(detail=True, methods=['get'], url_path='check_verification')
    def check_verification(self, request, pk=None):
        """
        Checks if the current user is verified for a specific service.
        This means they can leave reviews.
        """
        service = self.get_object()
        user = request.user
        
        # Business users can't be verified for services
        if user.is_business:
            return Response({'is_verified': False})
        
        # Check if the user is in the verified_customers list
        is_verified = VerifiedServiceCustomer.objects.filter(
            service=service,
            customer=user
        ).exists()
        
        # If not verified via VerifiedServiceCustomer, check for closed inquiries
        if not is_verified:
            # Check if the user has a closed inquiry for this service
            inquiry = Inquiry.objects.filter(
                service=service,
                customer=user,
                status=Inquiry.Status.CLOSED
            ).first()
            
            if inquiry:
                # Create verification record based on closed inquiry
                VerifiedServiceCustomer.objects.create(
                    service=service,
                    customer=user,
                    verified_by=inquiry.moderator
                )
                is_verified = True
        
        return Response({'is_verified': is_verified})
    
    @action(detail=False, methods=['get'], url_path='my_services')
    def my_services(self, request):
        """
        Returns all services created by the current business user
        """
        if not request.user.is_business:
            return Response(
                {'error': 'Only business users can access their services'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        services = Service.objects.filter(business=request.user)
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Returns statistics for a business user's services:
        - Number of active listings
        - Total bookings (inquiries)
        - Total reviews
        - Average rating
        """
        if not request.user.is_business:
            return Response(
                {'error': 'Only business users can access service statistics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Count active listings
        active_listings = Service.objects.filter(business=request.user).count()
        
        # Count total inquiries
        total_bookings = Inquiry.objects.filter(
            service__business=request.user
        ).count()
        
        # Count total reviews
        reviews = Review.objects.filter(
            service__business=request.user
        )
        total_reviews = reviews.count()
        
        # Calculate average rating across all services
        avg_rating = 0
        if total_reviews > 0:
            avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            if avg_rating:
                avg_rating = round(avg_rating, 1)
        
        # Count verified customers
        verified_customers_count = VerifiedServiceCustomer.objects.filter(
            service__business=request.user
        ).count()
        
        return Response({
            'active_listings': active_listings,
            'total_bookings': total_bookings,
            'total_reviews': total_reviews,
            'avg_rating': avg_rating,
            'verified_customers': verified_customers_count
        })


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
    
    @action(detail=True, methods=['get'])
    def service(self, request, pk=None):
        """
        Returns the service ID for an inquiry, useful for frontend verification
        """
        inquiry = self.get_object()
        
        # Check if the customer is verified for this service
        is_verified = VerifiedServiceCustomer.objects.filter(
            service=inquiry.service,
            customer=inquiry.customer
        ).exists()
        
        # If not verified via VerifiedServiceCustomer, check if inquiry is closed
        if not is_verified and inquiry.status == Inquiry.Status.CLOSED:
            # Create verification record if closed inquiry
            VerifiedServiceCustomer.objects.create(
                service=inquiry.service,
                customer=inquiry.customer,
                verified_by=inquiry.moderator
            )
            is_verified = True
        
        return Response({
            'service_id': inquiry.service.id,
            'service_name': inquiry.service.name,
            'is_verified': is_verified
        })


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

class IsReviewOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a review to update or delete it.
    
    Read permissions are allowed to any authenticated user.
    Write permissions are restricted to the user who created the review.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the review
        return obj.user == request.user


class IsReviewCommentAllowed(permissions.BasePermission):
    """
    Custom permission for review comments.
    
    Only allows service owners and moderators to create/edit/delete comments.
    """
    def has_permission(self, request, view):
        # For listing/viewing, anyone can access
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # For write operations, check if user is service owner or moderator
        # This requires getting the review object from the URL
        if view.kwargs.get('review_pk'):
            try:
                review = Review.objects.get(review_id=view.kwargs['review_pk'])
                return (request.user == review.service.business or 
                        request.user.is_moderator)
            except Review.DoesNotExist:
                return False
        return False
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only author (service owner or moderator) can edit their comments
        return obj.author == request.user


class ServiceReviewListView(generics.ListAPIView):
    """
    API endpoint for listing all reviews for a specific service.
    
    GET: Returns all reviews for the service specified in the URL.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        """Return reviews for the specified service"""
        service_id = self.kwargs.get('service_pk')
        return Review.objects.filter(service__id=service_id)


class UserReviewListView(generics.ListAPIView):
    """
    API endpoint for listing all reviews by a specific user.
    
    GET: Returns all reviews written by the user specified in the URL.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        """Return reviews by the specified user"""
        user_id = self.kwargs.get('user_pk')
        return Review.objects.filter(user__id=user_id)


class ServiceReviewCreateView(generics.CreateAPIView):
    """
    API endpoint for creating a review for a specific service.
    
    POST: Creates a new review for the service specified in the URL.
           Only users with closed inquiries for the service can create reviews.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewSerializer
    
    def get_serializer_context(self):
        """Add the service to the serializer context"""
        context = super().get_serializer_context()
        service_id = self.kwargs.get('service_pk')
        context['service'] = Service.objects.get(id=service_id)
        return context
    
    def get_serializer(self, *args, **kwargs):
        """Pre-populate the service field in the serializer data"""
        if kwargs.get('data') and not kwargs['data'].get('service'):
            service_id = self.kwargs.get('service_pk')
            if isinstance(kwargs['data'], dict):
                kwargs['data']['service'] = service_id
            else:
                # Handle immutable QueryDict by copying it
                data = kwargs['data'].copy()
                data['service'] = service_id
                kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)
    
    def perform_create(self, serializer):
        """Set the service and user from the URL and request"""
        service_id = self.kwargs.get('service_pk')
        service = Service.objects.get(id=service_id)
        serializer.save(user=self.request.user, service=service)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific review.
    
    GET: Retrieve the review details
    PUT/PATCH: Update the review (only allowed for the review owner)
    DELETE: Delete the review (only allowed for the review owner)
    """
    permission_classes = [permissions.IsAuthenticated, IsReviewOwner]
    serializer_class = ReviewSerializer
    lookup_url_kwarg = 'review_pk'
    
    def get_queryset(self):
        """Get the review, optionally filtering by service"""
        service_id = self.kwargs.get('service_pk')
        if service_id:
            return Review.objects.filter(service__id=service_id)
        return Review.objects.all()


class ReviewCommentListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating comments on a specific review.
    
    GET: List all comments for a review
    POST: Create a new comment (only allowed for service owners and moderators)
    """
    permission_classes = [permissions.IsAuthenticated, IsReviewCommentAllowed]
    serializer_class = ReviewCommentSerializer
    
    def get_queryset(self):
        """Return comments for the specified review"""
        review_id = self.kwargs.get('review_pk')
        return ReviewComment.objects.filter(review__review_id=review_id)
    
    def get_serializer_context(self):
        """Add the review to the serializer context"""
        context = super().get_serializer_context()
        review_id = self.kwargs.get('review_pk')
        try:
            context['review'] = Review.objects.get(review_id=review_id)
        except Review.DoesNotExist:
            pass
        return context
    
    def get_serializer(self, *args, **kwargs):
        """Pre-populate the review field in the serializer data"""
        if kwargs.get('data') and not kwargs['data'].get('review'):
            review_id = self.kwargs.get('review_pk')
            if isinstance(kwargs['data'], dict):
                kwargs['data']['review'] = review_id
            else:
                # Handle immutable QueryDict by copying it
                data = kwargs['data'].copy()
                data['review'] = review_id
                kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)
    
    def perform_create(self, serializer):
        """Set the review and author based on URL and request"""
        review_id = self.kwargs.get('review_pk')
        review = Review.objects.get(review_id=review_id)
        serializer.save(author=self.request.user, review=review)


class ReviewCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for managing a specific comment on a review.
    
    GET: Retrieve the comment
    PUT/PATCH: Update the comment (only allowed for the comment author)
    DELETE: Delete the comment (only allowed for the comment author)
    """
    permission_classes = [permissions.IsAuthenticated, IsReviewCommentAllowed]
    serializer_class = ReviewCommentSerializer
    lookup_url_kwarg = 'comment_pk'
    
    def get_queryset(self):
        """Get the comment, filtering by review"""
        review_id = self.kwargs.get('review_pk')
        return ReviewComment.objects.filter(review__review_id=review_id)


from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog categories.
    
    Allows listing, creating, retrieving, updating, and deleting blog categories.
    Only moderators can create, update, or delete categories.
    """
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """
        Allow anyone to view categories, but only moderators to modify them
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsModeratorUser()]
        return [permissions.IsAuthenticated()]


class IsAuthorOrModeratorPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or moderators to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if user is author or moderator
        return obj.author == request.user or request.user.is_moderator


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for blog posts.
    
    Allows listing, creating, retrieving, updating, and deleting blog posts.
    Only the author or moderators can update or delete posts.
    """
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrModeratorPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'content', 'summary', 'author__username']
    ordering_fields = ['created_at', 'updated_at', 'views']
    ordering = ['-created_at']
    filterset_fields = ['author', 'category', 'is_published']
    
    def get_queryset(self):
        """
        Filter queryset based on user and published status.
        
        - Moderators see all posts
        - Authors see their own posts (published and unpublished)
        - Everyone else sees only published posts
        """
        user = self.request.user
        
        # Base queryset
        queryset = BlogPost.objects.all()
        
        # If user is moderator, show all posts
        if user.is_moderator:
            return queryset
            
        # For regular users, show all published posts plus their own unpublished posts
        return queryset.filter(
            Q(is_published=True) | Q(author=user)
        )
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action == 'create':
            return BlogPostCreateSerializer
        return BlogPostDetailSerializer
    
    def perform_create(self, serializer):
        """Set author to current user"""
        serializer.save(author=self.request.user)
    
    def perform_update(self, serializer):
        """Track when post is updated"""
        serializer.save(updated_at=timezone.now())
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a blog post"""
        instance = self.get_object()
        # Only increment views for published posts and not from the author
        if instance.is_published and instance.author != request.user:
            instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BlogPostBySlugView(generics.RetrieveAPIView):
    """
    API view for retrieving a blog post by its slug.
    This provides a more SEO-friendly URL for accessing posts.
    """
    serializer_class = BlogPostDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    
    def get_queryset(self):
        """
        Filter queryset based on user and published status, similar to viewset.
        """
        user = self.request.user
        
        if user.is_moderator:
            return BlogPost.objects.all()
            
        return BlogPost.objects.filter(
            Q(is_published=True) | Q(author=user)
        )
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a blog post"""
        instance = self.get_object()
        # Only increment views for published posts and not from the author
        if instance.is_published and instance.author != request.user:
            instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserBlogPostListView(generics.ListAPIView):
    """
    API view for listing blog posts by a specific user.
    """
    serializer_class = BlogPostListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'summary']
    ordering_fields = ['created_at', 'updated_at', 'views']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter blog posts by user ID from URL and published status.
        """
        user_pk = self.kwargs.get('user_pk')
        current_user = self.request.user
        target_user = get_object_or_404(User, pk=user_pk)
        
        # Determine which posts should be visible
        if current_user.is_moderator or current_user == target_user:
            # Moderators and post authors see all posts
            return BlogPost.objects.filter(author=target_user)
        else:
            # Others see only published posts
            return BlogPost.objects.filter(author=target_user, is_published=True)


class BlogCommentListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating blog comments.
    """
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter comments by blog post ID from URL"""
        blog_post_pk = self.kwargs.get('blog_post_pk')
        return BlogComment.objects.filter(blog_post_id=blog_post_pk)
    
    def perform_create(self, serializer):
        """Set blog post and author when creating a comment"""
        blog_post_pk = self.kwargs.get('blog_post_pk')
        blog_post = get_object_or_404(BlogPost, pk=blog_post_pk)
        
        # Check if the blog post exists and is accessible
        if not blog_post.is_published:
            user = self.request.user
            if user != blog_post.author and not user.is_moderator:
                raise ValidationError("Cannot comment on unpublished blog posts")
                
        serializer.save(
            blog_post=blog_post,
            author=self.request.user
        )
        
    def get_serializer(self, *args, **kwargs):
        """Pre-populate the blog_post field in the serializer data"""
        if kwargs.get('data') and not kwargs['data'].get('blog_post'):
            blog_post_pk = self.kwargs.get('blog_post_pk')
            if isinstance(kwargs['data'], dict):
                kwargs['data']['blog_post'] = blog_post_pk
            else:
                # Handle immutable QueryDict by copying it
                data = kwargs['data'].copy()
                data['blog_post'] = blog_post_pk
                kwargs['data'] = data
        return super().get_serializer(*args, **kwargs)


class BlogCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a specific blog comment.
    """
    queryset = BlogComment.objects.all()
    serializer_class = BlogCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrModeratorPermission]
    lookup_url_kwarg = 'comment_pk'
    
    def get_object(self):
        """Get the comment by its ID from the URL"""
        comment_pk = self.kwargs.get('comment_pk')
        comment = get_object_or_404(BlogComment, pk=comment_pk)
        
        # Check permissions
        self.check_object_permissions(self.request, comment)
        return comment


class ModeratorListView(generics.ListAPIView):
    """
    API endpoint for listing all moderators with their active inquiry counts.
    Excludes admin users from the list.
    """
    serializer_class = ModeratorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return all users with the moderator role, excluding admins"""
        return User.objects.filter(
            role=User.Role.MODERATOR,
            is_staff=False,
            is_superuser=False
        )


class ModeratorRequestView(generics.CreateAPIView):
    """
    API endpoint for requesting a moderator for an inquiry.
    
    This allows customers and businesses to explicitly request moderators
    for active inquiries.
    """
    serializer_class = ModeratorRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        inquiry = serializer.save()
        return inquiry


class PaymentRequestListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating payment requests.
    
    GET:
    - For business users: Returns payment requests they've created
    - For customers: Returns payment requests directed to them
    - For moderators: Returns all payment requests
    
    POST (business users only):
    - Creates a new payment request for a customer in an existing inquiry
    """
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'inquiry']
    ordering_fields = ['created_at', 'updated_at', 'amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter payment requests based on user role"""
        user = self.request.user
        
        # Moderators can see all payment requests
        if user.is_moderator:
            return PaymentRequest.objects.all()
            
        # Business users can see payment requests they created
        if user.is_business:
            return PaymentRequest.objects.filter(creator=user)
            
        # Customers can see payment requests directed to them
        return PaymentRequest.objects.filter(recipient=user)
        
    def perform_create(self, serializer):
        """Create a payment request with the current user as creator"""
        if not self.request.user.is_business:
            raise permissions.PermissionDenied("Only business users can create payment requests")
            
        serializer.save(creator=self.request.user)


class PaymentRequestDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving details of a payment request.
    
    GET: Returns the details of a specific payment request.
    """
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'request_id'
    lookup_url_kwarg = 'request_id'
    
    def get_queryset(self):
        """Filter payment requests based on user role"""
        user = self.request.user
        
        # Moderators can see all payment requests
        if user.is_moderator:
            return PaymentRequest.objects.all()
            
        # Business users can see payment requests they created
        if user.is_business:
            return PaymentRequest.objects.filter(creator=user)
            
        # Customers can see payment requests directed to them
        return PaymentRequest.objects.filter(recipient=user)


class PendingPaymentRequestListView(generics.ListAPIView):
    """
    API endpoint for listing pending payment requests for the authenticated user.
    
    GET: Returns all pending payment requests directed to the authenticated user.
    """
    serializer_class = PaymentRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return pending payment requests for the current user"""
        return PaymentRequest.objects.filter(
            recipient=self.request.user,
            status=PaymentRequest.Status.PENDING
        ).order_by('-created_at')


class PaymentRequestActionView(generics.GenericAPIView):
    """
    API endpoint for accepting or declining a payment request.
    
    POST: Accepts or declines a payment request based on the action parameter.
    """
    serializer_class = PaymentRequestActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the payment request by its request_id from the URL"""
        request_id = self.kwargs.get('request_id')
        payment_request = get_object_or_404(PaymentRequest, request_id=request_id)
        
        # Check if user is the recipient
        if payment_request.recipient != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only respond to payment requests sent to you")
            
        return payment_request
    
    def post(self, request, *args, **kwargs):
        """Process the payment request action"""
        payment_request = self.get_object()
        
        # Add payment request to serializer context
        serializer = self.get_serializer(data=request.data)
        serializer.context['payment_request'] = payment_request
        
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        
        try:
            if action == 'accept':
                # Accept and process the payment
                transaction = payment_request.accept()
                return Response({
                    'message': 'Payment request accepted',
                    'transaction_id': str(transaction.transaction_id),
                    'amount': str(payment_request.amount),
                    'new_balance': str(request.user.wallet.balance)
                })
            elif action == 'decline':
                # Decline the payment request
                payment_request.decline()
                return Response({
                    'message': 'Payment request declined'
                })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class IsConversationParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to view or interact with it.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user == obj.sender or user == obj.recipient


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating conversations.
    
    GET: Returns all conversations the authenticated user is a participant in.
    POST: Creates a new conversation with the authenticated user as the sender.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationSerializer
    
    def get_queryset(self):
        """Return conversations where the user is either sender or recipient"""
        user = self.request.user
        return Conversation.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient')
    
    def post(self, request, *args, **kwargs):
        """Create a new conversation with initial message"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        # Return the created conversation with full details
        conversation_serializer = ConversationSerializer(
            result['conversation'],
            context={'request': request}
        )
        
        return Response(conversation_serializer.data, status=status.HTTP_201_CREATED)


class ConversationDetailView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific conversation.
    
    GET: Returns the details of a conversation the user is a participant in.
    """
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]
    lookup_field = 'conversation_id'
    lookup_url_kwarg = 'conversation_id'
    
    def get_queryset(self):
        """Return conversations where the user is either sender or recipient"""
        user = self.request.user
        return Conversation.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient')


class ConversationActionView(generics.GenericAPIView):
    """
    API endpoint for accepting or denying a conversation request.
    
    POST: Accepts or denies a conversation request based on the action parameter.
    """
    serializer_class = ConversationActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the conversation by its conversation_id from the URL"""
        conversation_id = self.kwargs.get('conversation_id')
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        
        # Check if user is the recipient
        if conversation.recipient != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only respond to conversation requests sent to you")
            
        return conversation
    
    def post(self, request, *args, **kwargs):
        """Process the conversation action"""
        conversation = self.get_object()
        
        # Add conversation to serializer context
        serializer = self.get_serializer(data=request.data)
        serializer.context['conversation'] = conversation
        
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data['action']
        
        try:
            if action == 'accept':
                # Accept and process the payment
                transaction = conversation.accept()
                return Response({
                    'message': 'Conversation request accepted',
                    'transaction_id': str(transaction.transaction_id),
                    'amount': "5.00",  # Fixed 5€ fee
                    'conversation_id': str(conversation.conversation_id),
                    'new_balance': str(conversation.sender.wallet.balance)
                })
            elif action == 'deny':
                # Deny the conversation request
                result = conversation.deny()
                return Response({
                    'message': 'Conversation request denied',
                    'conversation_id': str(result['conversation_id'])
                })
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ConversationMessageListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating messages within a conversation.
    
    GET: Returns all messages in a specific conversation.
    POST: Creates a new message in the conversation.
    """
    serializer_class = ConversationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return messages for a specific conversation, marking unread ones as read"""
        user = self.request.user
        conversation_id = self.kwargs.get('conversation_id')
        
        # Check if user is a participant in this conversation
        conversation = get_object_or_404(
            Conversation.objects.filter(Q(sender=user) | Q(recipient=user)), 
            conversation_id=conversation_id
        )
        
        # Mark messages from the other user as read
        if self.request.method == 'GET':
            unread_messages = ConversationMessage.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=user)
            
            for message in unread_messages:
                message.mark_as_read()
        
        return ConversationMessage.objects.filter(
            conversation__conversation_id=conversation_id
        ).select_related('sender')
    
    def perform_create(self, serializer):
        """Create a message in the specified conversation"""
        conversation_id = self.kwargs.get('conversation_id')
        user = self.request.user
        
        # Get the conversation
        conversation = get_object_or_404(
            Conversation, 
            conversation_id=conversation_id
        )
        
        # Check if user is a participant
        if not (user == conversation.sender or user == conversation.recipient):
            raise serializers.ValidationError("You are not a participant in this conversation")
            
        # Check if the conversation is accepted
        if not conversation.is_accepted:
            raise serializers.ValidationError("Cannot send messages in a conversation that has not been accepted")
            
        # Create the message
        serializer.save(
            sender=user,
            conversation=conversation
        )
        
        # Update the conversation's updated_at timestamp
        conversation.save(update_fields=['updated_at'])


class UnreadConversationCountView(generics.GenericAPIView):
    """
    API endpoint for getting the count of conversations with unread messages.
    
    GET: Returns the count of conversations with unread messages for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get the count of conversations with unread messages"""
        user = request.user
        
        # Get all conversations where the user is a participant
        conversations = Conversation.objects.filter(
            Q(sender=user) | Q(recipient=user),
            is_accepted=True
        )
        
        # Count conversations with unread messages
        unread_count = 0
        for conversation in conversations:
            # Check if there are unread messages from the other user
            has_unread = ConversationMessage.objects.filter(
                conversation=conversation,
                is_read=False
            ).exclude(sender=user).exists()
            
            if has_unread:
                unread_count += 1
        
        return Response({'unread_count': unread_count})


# Support Ticket views
class SupportTicketListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating support tickets.
    
    GET: Returns all support tickets the authenticated user has access to.
    POST: Creates a new support ticket with an initial message.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SupportTicketCreateSerializer
        return SupportTicketSerializer
    
    def get_queryset(self):
        """Return tickets based on user role"""
        user = self.request.user
        
        if user.is_moderator:
            # Moderators can see all tickets
            return SupportTicket.objects.all()
        else:
            # Regular users can only see their own tickets
            return SupportTicket.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """Create a new support ticket with an initial message"""
        serializer.save()
        # No need to return anything, serializer.data will be used in the response


class SupportTicketDetailView(generics.RetrieveAPIView):
    """
    API endpoint for accessing a specific support ticket.
    
    GET: Returns details about a specific support ticket.
    """
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'ticket_id'
    lookup_url_kwarg = 'ticket_id'
    
    def get_queryset(self):
        """Return tickets based on user role and permissions"""
        user = self.request.user
        
        if user.is_moderator:
            # Moderators can see all tickets
            return SupportTicket.objects.all()
        else:
            # Regular users can only see their own tickets
            return SupportTicket.objects.filter(user=user)


class SupportTicketCloseView(generics.GenericAPIView):
    """
    API endpoint for closing a support ticket.
    
    POST: Closes a support ticket (moderators only).
    """
    serializer_class = SupportTicketCloseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get the ticket by ID and check moderator permissions"""
        ticket_id = self.kwargs.get('ticket_id')
        ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
            
        # Check if the user is a moderator
        if not self.request.user.is_moderator:
            raise PermissionDenied("Only moderators can close support tickets")
                
        return ticket
    
    def post(self, request, *args, **kwargs):
        """Close a support ticket"""
        ticket = self.get_object()
        
        # Check if the ticket is already closed
        if ticket.status == SupportTicket.Status.CLOSED:
            return Response(
                {"error": "This ticket is already closed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create serializer with the empty data
        serializer = self.get_serializer(
            data={},
            context={'ticket': ticket, 'request': request}
        )
        
        if serializer.is_valid():
            # Close the ticket
            ticket.close(request.user)
            updated_serializer = SupportTicketSerializer(ticket)
            return Response(updated_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupportMessageListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating support ticket messages.
    
    GET: Returns all messages in a support ticket.
    POST: Creates a new message in a support ticket.
    """
    serializer_class = SupportMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Override create to log request data and handle errors"""
        print("Create support message request data:", request.data)
        
        # Validate that content is present
        if not request.data.get('content'):
            return Response(
                {"detail": "Content field is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print("Error creating support message:", str(e))
            return Response(
                {"detail": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get_ticket(self):
        """Get the ticket by ID and check permissions"""
        ticket_id = self.kwargs.get('ticket_id')
        try:
            ticket = SupportTicket.objects.get(ticket_id=ticket_id)
            
            # Check if the user is allowed to access this ticket
            user = self.request.user
            if not user.is_moderator and user != ticket.user:
                raise PermissionDenied("You do not have permission to access this ticket")
                
            return ticket
        except SupportTicket.DoesNotExist:
            raise Http404("Support ticket not found")
    
    def get_queryset(self):
        """Return messages for a specific ticket, marking unread ones as read"""
        ticket = self.get_ticket()
        user = self.request.user
        
        # Mark messages as read for this user
        if self.request.method == 'GET':
            if user.is_moderator:
                # If moderator, mark customer messages as read
                SupportMessage.objects.filter(
                    ticket=ticket,
                    sender=ticket.user,
                    is_read=False
                ).update(is_read=True)
            else:
                # If customer, mark moderator messages as read
                # Get a list of moderators
                from django.contrib.auth import get_user_model
                User = get_user_model()
                moderator_ids = User.objects.filter(role=User.Role.MODERATOR).values_list('id', flat=True)
                
                SupportMessage.objects.filter(
                    ticket=ticket,
                    sender__id__in=moderator_ids,
                    is_read=False
                ).update(is_read=True)
        
        return SupportMessage.objects.filter(ticket=ticket)
    
    def perform_create(self, serializer):
        """Create a new message in the specified ticket"""
        ticket = self.get_ticket()
        
        # Check if ticket is closed
        if ticket.status == SupportTicket.Status.CLOSED:
            raise serializers.ValidationError("This ticket is closed, you cannot add more messages")
        
        serializer.save(
            ticket=ticket,
            sender=self.request.user
        )


class SupportUnreadCountView(generics.GenericAPIView):
    """
    API endpoint for getting the unread support message count.
    
    GET: Returns the number of unread support messages for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get unread support message count"""
        user = request.user
        
        if user.is_moderator:
            # For moderators, count unread messages from all tickets
            # Either assigned to this moderator or unassigned (null moderator)
            from django.db.models import Q
            tickets = SupportTicket.objects.filter(
                Q(moderator=user) | Q(moderator__isnull=True)
            )
            
            # Get count of unread messages from non-moderators
            unread_count = SupportMessage.objects.filter(
                ticket__in=tickets,
                sender__role=User.Role.CUSTOMER,  # More direct than using a subquery
                is_read=False
            ).count()
        else:
            # For regular users, count unread messages from moderators
            # Get a list of moderators
            from django.contrib.auth import get_user_model
            User = get_user_model()
            moderator_ids = User.objects.filter(role=User.Role.MODERATOR).values_list('id', flat=True)
            
            unread_count = SupportMessage.objects.filter(
                ticket__user=user,
                sender__id__in=moderator_ids,
                is_read=False
            ).count()
        
        return Response({'unread_count': unread_count})