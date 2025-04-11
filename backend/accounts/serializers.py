# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from django.db import models
from decimal import Decimal
from .models import (
    Wallet, Transaction, Service, Inquiry, InquiryMessage,
    Review, ReviewComment, Category, BlogCategory, BlogPost, BlogComment,
    PaymentRequest, Conversation, ConversationMessage
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id", 
            "email", 
            "username", 
            "password", 
            "first_name", 
            "last_name", 
            "role", 
            "role_display",
            "profile_image",
            "bio",
            "expertise"
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"required": False},
            "profile_image": {"required": False},
            "bio": {"required": False},
            "expertise": {"required": False},
        }

    def create(self, validated_data):
        if "username" not in validated_data:
            # Set username to email if not provided
            validated_data["username"] = validated_data["email"]

        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    is_business = serializers.BooleanField(read_only=True)
    is_moderator = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "role_display",
            "is_business",
            "is_moderator",
            "profile_image",
            "bio",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login", "is_business", "is_moderator"]
        extra_kwargs = {
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        
    def update(self, instance, validated_data):
        """Handle profile image updates properly"""
        # Pop profile_image if it exists to handle it specially
        profile_image = validated_data.pop('profile_image', None)
        
        # If profile_image is None, and it's explicitly included in validated_data,
        # that means the user wants to remove their profile image
        if profile_image is None and 'profile_image' in self.initial_data:
            instance.profile_image = None
        elif profile_image:
            instance.profile_image = profile_image
            
        # Update the rest of the fields normally
        return super().update(instance, validated_data)
        
    def validate(self, data):
        # Role changes logic
        if 'role' in data and data['role'] != self.instance.role:
            current_role = self.instance.role
            new_role = data['role']
            user = self.instance
            
            # No one can become a moderator through this API
            if new_role == User.Role.MODERATOR:
                raise serializers.ValidationError({'role': 'Cannot change role to moderator'})
                
            # Moderators cannot change their role
            if current_role == User.Role.MODERATOR:
                raise serializers.ValidationError({'role': 'Moderators cannot change their role'})
                
            # Business to Customer: must close all inquiries and delete services
            if current_role == User.Role.BUSINESS and new_role == User.Role.CUSTOMER:
                # Check if user has any open inquiries for their services
                open_inquiries = Inquiry.objects.filter(
                    service__business=user,
                    status=Inquiry.Status.OPEN
                ).exists()
                
                if open_inquiries:
                    raise serializers.ValidationError(
                        {'role': 'You must close all open inquiries before changing to customer role'}
                    )
                
                # Check if user has any services
                has_services = Service.objects.filter(business=user).exists()
                if has_services:
                    raise serializers.ValidationError(
                        {'role': 'You must delete all your services before changing to customer role'}
                    )
                    
            # Customer can become Business without restrictions
            if current_role == User.Role.CUSTOMER and new_role == User.Role.BUSINESS:
                # No restrictions, allowed to change
                pass
            
        return data


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user_email", "username", "balance", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "user_email",
            "username",
            "balance",
            "created_at",
            "updated_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    from_email = serializers.EmailField(
        source="from_wallet.user.email", read_only=True, allow_null=True
    )
    to_email = serializers.EmailField(
        source="to_wallet.user.email", read_only=True, allow_null=True
    )
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "from_wallet",
            "to_wallet",
            "from_email",
            "to_email",
            "amount",
            "transaction_type",
            "transaction_type_display",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "from_wallet",
            "to_wallet",
            "amount",
            "transaction_type",
            "created_at",
        ]


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    recipient_email = serializers.EmailField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


# for login process, replaces the default username field with email
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model"""
    
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ServiceSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.username', read_only=True)
    business_image = serializers.ImageField(source='business.profile_image', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "logo",
            "category",
            "category_name",
            "business",
            "business_name",
            "business_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["business", "created_at", "updated_at"]
    
    def create(self, validated_data):
        # Set the business to the current user
        user = self.context['request'].user
        if not user.is_business:
            raise serializers.ValidationError("Only business users can create services")
        validated_data['business'] = user
        return super().create(validated_data)
        
    def update(self, instance, validated_data):
        """Handle logo updates properly"""
        # Pop logo if it exists to handle it specially
        logo = validated_data.pop('logo', None)
        
        # If logo is None, and it's explicitly included in validated_data,
        # that means the user wants to remove their logo
        if logo is None and 'logo' in self.initial_data:
            instance.logo = None
        elif logo:
            instance.logo = logo
            
        # Update the rest of the fields normally
        return super().update(instance, validated_data)


class InquiryMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_role = serializers.CharField(source='sender.get_role_display', read_only=True)
    
    class Meta:
        model = InquiryMessage
        fields = [
            "id",
            "inquiry",
            "sender",
            "sender_name",
            "sender_role",
            "content",
            "created_at",
        ]
        read_only_fields = ["sender", "created_at"]
    
    def create(self, validated_data):
        # Set the sender to the current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class InquirySerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    business_name = serializers.CharField(source='service.business.username', read_only=True)
    customer_name = serializers.CharField(source='customer.username', read_only=True)
    moderator_name = serializers.CharField(source='moderator.username', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    messages = InquiryMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Inquiry
        fields = [
            "id",
            "service",
            "service_name",
            "business_name",
            "customer",
            "customer_name",
            "moderator",
            "moderator_name",
            "subject",
            "status",
            "status_display",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["customer", "moderator", "status", "created_at", "updated_at"]
    
    def create(self, validated_data):
        # Set the customer to the current user
        validated_data['customer'] = self.context['request'].user
        validated_data['status'] = Inquiry.Status.OPEN
        return super().create(validated_data)


class InquiryCreateSerializer(serializers.ModelSerializer):
    initial_message = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Inquiry
        fields = ["service", "subject", "initial_message"]
    
    def create(self, validated_data):
        initial_message = validated_data.pop('initial_message')
        
        # Set the customer to the current user
        user = self.context['request'].user
        validated_data['customer'] = user
        
        # Check if the user is trying to create an inquiry for their own service
        service = validated_data.get('service')
        if service and service.business == user:
            raise serializers.ValidationError("You cannot create an inquiry for your own service")
        
        # Create the inquiry without assigning a moderator
        inquiry = Inquiry.objects.create(**validated_data)
        
        # Create the initial message
        InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=user,
            content=initial_message
        )
        
        return inquiry

class ReviewCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for review comments.
    
    Handles comments that service providers and moderators can make on reviews.
    """
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    
    class Meta:
        model = ReviewComment
        fields = [
            'comment_id', 'review', 'author', 'author_name', 'author_role',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['comment_id', 'created_at', 'updated_at', 'author']
    
    def validate(self, data):
        """
        Validates that only service owners and moderators can comment on reviews.
        """
        user = self.context['request'].user
        review = data.get('review')
        
        # Skip validation if review is not provided (it might be set in the view)
        if not review:
            return data
            
        # Check if user is the service owner or a moderator
        is_service_owner = (user == review.service.business)
        is_moderator = user.is_moderator
        
        if not (is_service_owner or is_moderator):
            raise serializers.ValidationError("Only service owners and moderators can comment on reviews.")
            
        return data
    
    def create(self, validated_data):
        """Sets the comment author to the current user"""
        validated_data['author'] = self.context['request'].user
        return ReviewComment.objects.create(**validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for service reviews.
    
    Handles validation, creation, and representation of review objects.
    Includes additional read-only fields and nested comments.
    """
    service_name = serializers.CharField(source='service.name', read_only=True)
    business_name = serializers.CharField(source='service.business.username', read_only=True)
    customer_name = serializers.CharField(source='user.username', read_only=True)
    comments = ReviewCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'service', 'service_name', 'business_name',
            'user', 'customer_name', 'rating', 'comment', 
            'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['review_id', 'created_at', 'updated_at', 'user', 'comments']
    
    def validate(self, data):
        """
        Custom validation that enforces business rules:
        
        1. Prevents duplicate reviews: a user can only review a service once
        2. Verifies the user has a closed inquiry for the service
        """
        user = self.context['request'].user
        service = data.get('service')
        
        # For updates, if service isn't being changed, skip service-related validations
        if self.instance and service is None:
            return data
            
        # Use the current service if not changing it during an update
        if self.instance and service is None:
            service = self.instance.service
        
        # Prevent duplicate reviews (only on creation)
        existing_review = Review.objects.filter(
            user=user,
            service=service
        ).exclude(review_id=getattr(self.instance, 'review_id', None))
        
        if existing_review.exists():
            raise serializers.ValidationError("You have already reviewed this service.")
        
        # Verify user has a closed inquiry for this service
        inquiry = Inquiry.objects.filter(
            customer=user,
            service=service,
            status=Inquiry.Status.CLOSED
        ).first()

        if not inquiry:
            raise serializers.ValidationError("You can only review a service if you have a closed inquiry for it.")
            
        return data
    
    def create(self, validated_data):
        """
        Creates a new review with the authenticated user as the author.
        This ensures the review is always tied to the current user.
        """
        validated_data['user'] = self.context['request'].user
        return Review.objects.create(**validated_data)


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'post_count']
        read_only_fields = ['created_at', 'updated_at', 'post_count']
    
    def get_post_count(self, obj):
        """Return count of published posts in this category"""
        return obj.blog_posts.filter(is_published=True).count()


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_role = serializers.CharField(source='author.get_role_display', read_only=True)
    author_image = serializers.ImageField(source='author.profile_image', read_only=True)
    
    class Meta:
        model = BlogComment
        fields = ['id', 'blog_post', 'author', 'author_name', 'author_role', 
                 'author_image', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Set the comment author to the current user"""
        validated_data['author'] = self.context['request'].user
        return BlogComment.objects.create(**validated_data)


class BlogPostListSerializer(serializers.ModelSerializer):
    """Serializer for listing blog posts with limited fields"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_image = serializers.ImageField(source='author.profile_image', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'summary', 'image', 'author', 'author_name', 
                 'author_image', 'category', 'category_name', 'created_at', 
                 'updated_at', 'views', 'comment_count', 'is_published']
        read_only_fields = ['slug', 'views', 'created_at', 'updated_at', 'comment_count', 'author']
    
    def get_comment_count(self, obj):
        """Return count of comments on this post"""
        return obj.comments.count()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed blog post view including comments"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_image = serializers.ImageField(source='author.profile_image', read_only=True)
    author_bio = serializers.CharField(source='author.bio', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comments = BlogCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'content', 'summary', 'image', 
                 'author', 'author_name', 'author_image', 'author_bio',
                 'category', 'category_name', 'created_at', 'updated_at', 
                 'is_published', 'views', 'comments']
        read_only_fields = ['slug', 'views', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure only authors and moderators can change publish status"""
        if 'is_published' in data and self.instance:
            user = self.context['request'].user
            is_author = user == self.instance.author
            is_moderator = user.is_moderator
            
            if not (is_author or is_moderator):
                raise serializers.ValidationError(
                    {"is_published": "Only the author or moderators can change publication status."}
                )
        return data


class BlogPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating blog posts with automatic slug generation"""
    slug = serializers.SlugField(read_only=True)
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'summary', 'image', 'category', 'is_published', 'slug', 'author']
        read_only_fields = ['slug', 'author']
    
    def create(self, validated_data):
        """Create blog post with the current user as author and generate slug"""
        # Set author to current user
        user = self.context['request'].user
        validated_data['author'] = user
        
        # Generate slug from title
        base_slug = slugify(validated_data['title'])
        slug = base_slug
        
        # Ensure slug is unique
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        validated_data['slug'] = slug
        
        # Create the blog post
        return BlogPost.objects.create(**validated_data)


class ModeratorSerializer(serializers.ModelSerializer):
    """Serializer for moderator information and activity"""
    active_inquiry_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_image',
            'active_inquiry_count',
        ]
        
    def get_active_inquiry_count(self, obj):
        """Return the count of active (open) inquiries assigned to this moderator"""
        return Inquiry.objects.filter(
            moderator=obj,
            status=Inquiry.Status.OPEN
        ).count()


class ModeratorRequestSerializer(serializers.Serializer):
    """Serializer for requesting a moderator for an inquiry"""
    inquiry_id = serializers.IntegerField()
    
    def validate_inquiry_id(self, value):
        """Validate that the inquiry exists and can have a moderator assigned"""
        try:
            inquiry = Inquiry.objects.get(pk=value)
        except Inquiry.DoesNotExist:
            raise serializers.ValidationError("Inquiry not found")
            
        # Check if user is a participant in this inquiry
        user = self.context['request'].user
        is_participant = (
            inquiry.customer == user or 
            inquiry.service.business == user
        )
        
        if not is_participant:
            raise serializers.ValidationError("You are not a participant in this inquiry")
            
        # Check if inquiry is still open
        if inquiry.status != Inquiry.Status.OPEN:
            raise serializers.ValidationError("Cannot request a moderator for a closed inquiry")
            
        # Check if inquiry already has a moderator
        if inquiry.moderator is not None:
            raise serializers.ValidationError("This inquiry already has a moderator assigned")
            
        # Check if a moderator request has already been made
        if inquiry.has_moderator_request:
            raise serializers.ValidationError("A moderator has already been requested for this inquiry")
            
        return value
        
    def save(self):
        """Process the moderator request"""
        inquiry_id = self.validated_data['inquiry_id']
        inquiry = Inquiry.objects.get(pk=inquiry_id)
        
        # Request and assign a moderator
        moderator = inquiry.request_moderator()
        return inquiry


class PaymentRequestSerializer(serializers.ModelSerializer):
    """Serializer for payment requests"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    service_name = serializers.CharField(source='inquiry.service.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    transaction_id = serializers.UUIDField(source='transaction.transaction_id', read_only=True, allow_null=True)
    
    class Meta:
        model = PaymentRequest
        fields = [
            'id',
            'request_id',
            'inquiry',
            'creator',
            'creator_name',
            'recipient',
            'recipient_name',
            'amount',
            'description',
            'status',
            'status_display',
            'service_name',
            'transaction',
            'transaction_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'request_id', 
            'creator', 
            'recipient', 
            'status', 
            'transaction',
            'created_at', 
            'updated_at'
        ]
    
    def validate(self, data):
        """Validate payment request data"""
        user = self.context['request'].user
        
        # Ensure user is a business
        if not user.is_business:
            raise serializers.ValidationError("Only business users can create payment requests")
        
        # Validate inquiry
        inquiry = data.get('inquiry')
        if inquiry:
            # Ensure the inquiry is open
            if inquiry.status != Inquiry.Status.OPEN:
                raise serializers.ValidationError("Cannot create payment requests for closed inquiries")
                
            # Ensure user owns the service in the inquiry
            if inquiry.service.business != user:
                raise serializers.ValidationError("You can only create payment requests for your own services")
        
        # Validate amount
        amount = data.get('amount')
        if amount and amount <= 0:
            raise serializers.ValidationError({"amount": "Amount must be positive"})
            
        return data
    
    def create(self, validated_data):
        """Create a payment request"""
        user = self.context['request'].user
        inquiry = validated_data['inquiry']
        
        # Set the creator and recipient
        validated_data['creator'] = user
        validated_data['recipient'] = inquiry.customer
        
        return PaymentRequest.objects.create(**validated_data)


class PaymentRequestActionSerializer(serializers.Serializer):
    """Serializer for accepting or declining payment requests"""
    action = serializers.ChoiceField(choices=['accept', 'decline'])
    
    def validate(self, data):
        """Validate the payment request action"""
        # The payment request object should be available in the context
        payment_request = self.context.get('payment_request')
        if not payment_request:
            raise serializers.ValidationError("Payment request not found")
            
        # Ensure the payment request is pending
        if payment_request.status != PaymentRequest.Status.PENDING:
            raise serializers.ValidationError(
                f"Cannot {data['action']} a payment request that is not pending"
            )
            
        # Ensure the user is the recipient of the payment request
        user = self.context['request'].user
        if payment_request.recipient != user:
            raise serializers.ValidationError("You can only respond to payment requests sent to you")
            
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing a user's password.
    Requires old password for security verification.
    New password must meet all password validation requirements.
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validate that the old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate_new_password(self, value):
        """Validate that the new password meets all requirements"""
        # Use Django's built-in password validators
        user = self.context['request'].user
        try:
            validate_password(value, user)
        except Exception as e:
            raise serializers.ValidationError(list(e))
        return value
    
    def validate(self, data):
        """Validate that new password and confirm password match"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': "Passwords don't match"})
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({'new_password': "New password cannot be the same as old password"})
            
        return data


class ConversationMessageSerializer(serializers.ModelSerializer):
    """Serializer for conversation messages"""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    is_sender = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationMessage
        fields = [
            'message_id', 
            'conversation', 
            'sender',
            'sender_id', 
            'sender_name',
            'content', 
            'created_at',
            'is_read',
            'is_sender'
        ]
        read_only_fields = ['message_id', 'sender', 'created_at', 'is_read']
    
    def get_is_sender(self, obj):
        """Check if the requesting user is the sender of this message"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False
    
    def create(self, validated_data):
        """Create a new message, setting the sender to the current user"""
        user = self.context['request'].user
        conversation = validated_data['conversation']
        
        # Verify the user is a participant in this conversation
        if not (user == conversation.sender or user == conversation.recipient):
            raise serializers.ValidationError("You are not a participant in this conversation")
            
        # Verify the conversation is accepted before allowing messages
        if not conversation.is_accepted:
            raise serializers.ValidationError("Cannot send messages in a conversation that has not been accepted")
            
        # Create the message
        validated_data['sender'] = user
        return ConversationMessage.objects.create(**validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    recipient_name = serializers.CharField(source='recipient.username', read_only=True)
    sender_image = serializers.ImageField(source='sender.profile_image', read_only=True)
    recipient_image = serializers.ImageField(source='recipient.profile_image', read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'sender',
            'sender_name',
            'sender_image',
            'recipient',
            'recipient_name',
            'recipient_image',
            'is_accepted',
            'created_at',
            'updated_at',
            'last_message',
            'unread_count'
        ]
        read_only_fields = [
            'conversation_id', 
            'is_accepted', 
            'created_at', 
            'updated_at'
        ]
    
    def get_last_message(self, obj):
        """Get the last message in the conversation"""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return {
                'id': last_message.message_id,
                'content': last_message.content[:50] + ('...' if len(last_message.content) > 50 else ''),
                'sender_name': last_message.sender.username,
                'timestamp': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        """Get the count of unread messages for the current user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return obj.messages.filter(is_read=False).exclude(sender=user).count()
        return 0
    
    def validate(self, data):
        """Validate conversation data"""
        # For creation only
        if not self.instance:
            sender = self.context['request'].user
            recipient = data.get('recipient')
            
            # Check if sender is trying to start a conversation with themselves
            if sender == recipient:
                raise serializers.ValidationError("You cannot start a conversation with yourself")
                
            # Check if a conversation already exists between these users
            existing_conversation = Conversation.objects.filter(
                (models.Q(sender=sender) & models.Q(recipient=recipient)) |
                (models.Q(sender=recipient) & models.Q(recipient=sender))
            ).first()
            
            if existing_conversation:
                raise serializers.ValidationError("A conversation already exists with this user")
                
        return data
    
    def create(self, validated_data):
        """Create a new conversation with the current user as sender"""
        validated_data['sender'] = self.context['request'].user
        return Conversation.objects.create(**validated_data)


class ConversationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new conversation with an initial message.
    This serializer handles the special case of starting a conversation
    from a review.
    """
    recipient_id = serializers.IntegerField(required=True)
    initial_message = serializers.CharField(required=True)
    review_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_recipient_id(self, value):
        """Validate that the recipient exists"""
        try:
            recipient = User.objects.get(pk=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
    
    def validate_review_id(self, value):
        """Validate that the review exists if provided"""
        if value:
            try:
                review = Review.objects.get(review_id=value)
                return value
            except Review.DoesNotExist:
                raise serializers.ValidationError("Review not found")
        return value
    
    def validate(self, data):
        """Validate the conversation request"""
        sender = self.context['request'].user
        recipient_id = data.get('recipient_id')
        review_id = data.get('review_id')
        
        try:
            recipient = User.objects.get(pk=recipient_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"recipient_id": "Recipient not found"})
        
        # Check if sender is trying to start a conversation with themselves
        if sender.id == recipient_id:
            raise serializers.ValidationError({"recipient_id": "You cannot start a conversation with yourself"})
        
        # Check if a conversation already exists between these users
        existing_conversation = Conversation.objects.filter(
            (models.Q(sender=sender) & models.Q(recipient=recipient)) |
            (models.Q(sender=recipient) & models.Q(recipient=sender))
        ).first()
        
        if existing_conversation:
            raise serializers.ValidationError({"recipient_id": "A conversation already exists with this user"})
        
        # If the request is coming from a review, validate that the recipient is actually the reviewer
        if review_id:
            try:
                review = Review.objects.get(review_id=review_id)
                if review.user.id != recipient_id:
                    raise serializers.ValidationError(
                        {"review_id": "The recipient must be the author of the specified review"}
                    )
            except Review.DoesNotExist:
                raise serializers.ValidationError({"review_id": "Review not found"})
        
        return data
    
    def create(self, validated_data):
        """
        Create a new conversation with the initial message.
        Returns both the conversation and the message objects.
        """
        sender = self.context['request'].user
        recipient_id = validated_data.get('recipient_id')
        initial_message = validated_data.get('initial_message')
        
        # Get the recipient user
        recipient = User.objects.get(pk=recipient_id)
        
        # Create the conversation
        conversation = Conversation.objects.create(
            sender=sender,
            recipient=recipient
        )
        
        # Create the initial message
        message = ConversationMessage.objects.create(
            conversation=conversation,
            sender=sender,
            content=initial_message
        )
        
        return {
            'conversation': conversation,
            'message': message
        }


class ConversationActionSerializer(serializers.Serializer):
    """Serializer for accepting or denying a conversation request"""
    action = serializers.ChoiceField(choices=['accept', 'deny'])
    
    def validate(self, data):
        """Validate the conversation action"""
        # The conversation object should be in the context
        conversation = self.context.get('conversation')
        user = self.context['request'].user
        
        if not conversation:
            raise serializers.ValidationError("Conversation not found")
            
        # Ensure the user is the recipient of the conversation request
        if conversation.recipient != user:
            raise serializers.ValidationError("You can only respond to conversation requests sent to you")
            
        # Ensure the conversation is not already accepted
        if conversation.is_accepted:
            raise serializers.ValidationError("This conversation has already been accepted")
            
        # If accepting, ensure the sender has sufficient funds
        if data['action'] == 'accept':
            sender_wallet = conversation.sender.wallet
            fee_amount = Decimal('5.00')  # 5€ fixed fee
            
            if sender_wallet.balance < fee_amount:
                raise serializers.ValidationError("The sender does not have sufficient funds for this conversation")
                
        return data