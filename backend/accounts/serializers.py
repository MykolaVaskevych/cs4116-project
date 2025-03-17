# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wallet, Transaction, Service, Inquiry, InquiryMessage, Review, ReviewComment
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "first_name", "last_name", "role", "role_display"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"required": False},
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
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login", "is_business", "is_moderator", "role"]
        extra_kwargs = {
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }
        
    def validate(self, data):
        # Role changes should be restricted
        if 'role' in data and data['role'] != self.instance.role:
            # Check if user is staff or superuser (admin)
            if not self.context['request'].user.is_staff and not self.context['request'].user.is_superuser:
                raise serializers.ValidationError({'role': 'You do not have permission to change your role'})
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


class ServiceSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source='business.username', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "business",
            "business_name",
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
        
        # Create the inquiry
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