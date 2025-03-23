from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import DO_NOTHING
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
import sys
import os

def resize_image(image_field, size=(512, 512)):
    """
    Resizes an image to the specified size and standardizes the format.
    Used for profile images and service logos.
    
    Args:
        image_field: The image field to resize
        size: Tuple of (width, height) for the output image
        
    Returns:
        The resized image as an InMemoryUploadedFile
    """
    if not image_field:
        return None
        
    img = Image.open(image_field)
    
    # Convert to RGB if image is RGBA (has transparency)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Resize the image while maintaining aspect ratio
    img.thumbnail(size, Image.LANCZOS)
    
    # If the image is not square, create a square image with white background
    if img.size[0] != img.size[1]:
        background = Image.new('RGB', size, (255, 255, 255))
        offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
        background.paste(img, offset)
        img = background
    
    # Save the image to a BytesIO object
    output = BytesIO()
    img.save(output, format='JPEG', quality=90)
    output.seek(0)
    
    # Create a new Django image object
    return InMemoryUploadedFile(
        output,
        'ImageField',
        f"{os.path.splitext(image_field.name)[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output),
        None
    )

class UserManager(DjangoUserManager):
    """Custom user manager that handles wallet creation"""
    
    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        Also creates associated wallet.
        """
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        
        # Use transaction.atomic to ensure both user and wallet are created or neither
        with transaction.atomic():
            user.save(using=self._db)
            # Create wallet directly here instead of using a signal
            # Use apps.get_model to avoid circular import
            from django.apps import apps
            Wallet = apps.get_model('accounts', 'Wallet')
            Wallet.objects.create(user=user)
            
        return user
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        # By default, set role to CUSTOMER if not provided
        extra_fields.setdefault("role", User.Role.CUSTOMER)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        # Set role to MODERATOR for superusers if not explicitly provided
        extra_fields.setdefault("role", User.Role.MODERATOR)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email for authentication
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer')
        BUSINESS = 'BUSINESS', _('Business')
        MODERATOR = 'MODERATOR', _('Moderator')
        
    # Override email field to make it unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    
    # Profile image
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True,
        help_text="User's profile avatar (512x512)"
    )
    
    # Optional biography
    bio = models.TextField(
        blank=True,
        help_text="User's biography or description"
    )
    
    # Use our custom manager that handles wallet creation
    objects = UserManager()
    
    # Make email the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Still required for admin creation
    
    def __str__(self):
        return self.email
        
    @property
    def is_business(self):
        return self.role == self.Role.BUSINESS
    
    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR
        
    def save(self, *args, **kwargs):
        """Override save method to resize profile image"""
        if self.profile_image:
            # Check if this is a new image or it has been changed
            if not self.pk or User.objects.get(pk=self.pk).profile_image != self.profile_image:
                self.profile_image = resize_image(self.profile_image)
        
        super().save(*args, **kwargs)


class Wallet(models.Model):
    """Wallet model associated with a user"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s wallet - {self.balance}"
    
    def deposit(self, amount):
        """Add funds to wallet and create transaction record"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Use atomic transaction to ensure both updates happen or none
        with transaction.atomic():
            # Get a lock on this wallet row
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            wallet.balance += amount
            wallet.save(update_fields=['balance', 'updated_at'])
            
            # Create transaction record
            tx = Transaction.objects.create(
                to_wallet=wallet,
                amount=amount,
                transaction_type=Transaction.TransactionType.DEPOSIT
            )
            
            # Update the instance
            self.balance = wallet.balance
            self.updated_at = wallet.updated_at
            
            return tx
        
    def withdraw(self, amount):
        """Withdraw funds from wallet and create transaction record"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Use atomic transaction to ensure both updates happen or none
        with transaction.atomic():
            # Get a lock on this wallet row
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")
                
            wallet.balance -= amount
            wallet.save(update_fields=['balance', 'updated_at'])
            
            # Create transaction record
            tx = Transaction.objects.create(
                from_wallet=wallet,
                amount=amount,
                transaction_type=Transaction.TransactionType.WITHDRAWAL
            )
            
            # Update the instance
            self.balance = wallet.balance
            self.updated_at = wallet.updated_at
            
            return tx
        
    def transfer(self, recipient_wallet, amount):
        """Transfer funds to another wallet and create transaction record"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        if self.balance < amount:
            raise ValueError("Insufficient funds")
            
        if self == recipient_wallet:
            raise ValueError("Cannot transfer to the same wallet")
        
        # Use transaction.atomic to ensure both wallets are updated or neither
        with transaction.atomic():
            # Update balances
            self.balance -= amount
            recipient_wallet.balance += amount
            self.save(update_fields=['balance', 'updated_at'])
            recipient_wallet.save(update_fields=['balance', 'updated_at'])
            
            # Create transaction record
            return Transaction.objects.create(
                from_wallet=self,
                to_wallet=recipient_wallet,
                amount=amount,
                transaction_type=Transaction.TransactionType.TRANSFER
            )


class Transaction(models.Model):
    """Model for tracking wallet transactions"""
    
    class TransactionType(models.TextChoices):
        DEPOSIT = 'DEPOSIT', _('Deposit')
        WITHDRAWAL = 'WITHDRAWAL', _('Withdrawal')
        TRANSFER = 'TRANSFER', _('Transfer')
    
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    from_wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE,
        related_name='sent_transactions',
        null=True,
        blank=True
    )
    to_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='received_transactions',
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} - {self.transaction_type}"
    
    def save(self, *args, **kwargs):
        # Validate transaction type and wallet relationships
        if self.transaction_type == self.TransactionType.DEPOSIT and self.from_wallet is not None:
            raise ValueError("Deposit transactions should not have a source wallet")
            
        if self.transaction_type == self.TransactionType.WITHDRAWAL and self.to_wallet is not None:
            raise ValueError("Withdrawal transactions should not have a destination wallet")
            
        if self.transaction_type == self.TransactionType.TRANSFER:
            if self.from_wallet is None or self.to_wallet is None:
                raise ValueError("Transfer transactions must have both source and destination wallets")
                
        super().save(*args, **kwargs)


class Category(models.Model):
    """
    Model for service categories.
    These are high-level groupings of services.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']


class Service(models.Model):
    """Model for business services that can be offered to customers"""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(
        upload_to='service_logos/', 
        null=True, 
        blank=True,
        help_text="Service logo image (512x512)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='services',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    business = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='services',
        limit_choices_to={'role': User.Role.BUSINESS}
    )
    
    def __str__(self):
        return f"{self.name} by {self.business.username}"
    
    def save(self, *args, **kwargs):
        # Ensure only business users can create services
        if not self.business.is_business:
            raise ValueError("Only business users can create services")
            
        # Resize logo if it exists and has changed
        if self.logo:
            if not self.pk or (Service.objects.filter(pk=self.pk).exists() and 
                              Service.objects.get(pk=self.pk).logo != self.logo):
                self.logo = resize_image(self.logo)
                
        super().save(*args, **kwargs)


class Inquiry(models.Model):
    """Model for customer inquiries about services"""
    
    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        CLOSED = 'CLOSED', _('Closed')
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_inquiries'
    )
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='moderated_inquiries',
        limit_choices_to={'role': User.Role.MODERATOR},
        null=True,
        blank=True
    )
    subject = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
    )
    has_moderator_request = models.BooleanField(
        default=False,
        help_text="Indicates if a moderator has been requested for this inquiry"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inquiry about {self.service.name} by {self.customer.username}"
    
    def close(self, moderator):
        """Close an inquiry - only moderators can do this"""
        if not moderator.is_moderator:
            raise ValueError("Only moderators can close inquiries")
        self.status = self.Status.CLOSED
        self.moderator = moderator
        self.save(update_fields=['status', 'moderator', 'updated_at'])
    
    def request_moderator(self):
        """Request a moderator for this inquiry"""
        if self.moderator is not None:
            raise ValueError("This inquiry already has a moderator assigned")
        if self.has_moderator_request:
            raise ValueError("A moderator has already been requested for this inquiry")
        
        self.has_moderator_request = True
        self.save(update_fields=['has_moderator_request', 'updated_at'])
        
        # Find the moderator with the fewest active inquiries
        User = get_user_model()
        moderators = User.objects.filter(role=User.Role.MODERATOR)
        
        if not moderators.exists():
            return None
            
        # Count active inquiries for each moderator
        moderator_counts = []
        for moderator in moderators:
            active_count = Inquiry.objects.filter(
                moderator=moderator,
                status=Inquiry.Status.OPEN
            ).count()
            moderator_counts.append((moderator, active_count))
        
        # Sort by count and assign the moderator with fewest inquiries
        moderator_counts.sort(key=lambda x: x[1])
        assigned_moderator = moderator_counts[0][0]
        
        # Assign the moderator
        self.moderator = assigned_moderator
        self.save(update_fields=['moderator', 'updated_at'])
        
        return assigned_moderator


class InquiryMessage(models.Model):
    """Model for messages within an inquiry"""
    
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message in {self.inquiry} by {self.sender.username}"
    
    class Meta:
        ordering = ['created_at']

class Review(models.Model):
    """
    Model for service reviews by customers.
    
    Reviews can only be created by customers who have a closed inquiry for the service.
    Each customer can only leave one review per service. Rating must be between 0-5.
    """
    review_id = models.AutoField(primary_key=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The service being reviewed"
    )
    user = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=DO_NOTHING,
        help_text="The customer who wrote the review"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        help_text="Rating from 0 to 5 stars"
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional review comment"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review for {self.service.name} by {self.user.username}"

    def save(self, *args, **kwargs):
        """
        Custom save method with business logic validation:
        1. Ensures the user has a closed inquiry for this service
        2. Prevents duplicate reviews for the same service by the same user
        """
        # Verify user has a closed inquiry for this service
        inquiry = Inquiry.objects.filter(
            customer=self.user, 
            service=self.service, 
            status=Inquiry.Status.CLOSED
        ).first()

        if not inquiry:
            raise ValueError("You can only review a service if you have a closed inquiry for it.")
            
        # Prevent duplicate reviews (only check on creation)
        if not self.pk and Review.objects.filter(user=self.user, service=self.service).exists():
            raise ValueError("You have already reviewed this service.")

        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']


class ReviewComment(models.Model):
    """
    Model for comments on reviews by service providers or moderators.
    
    These allow business owners to respond to reviews of their services,
    or moderators to add notes or mediate disputes.
    """
    comment_id = models.AutoField(primary_key=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="The review this comment is attached to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_comments',
        help_text="The user who wrote this comment (service owner or moderator)"
    )
    content = models.TextField(
        help_text="The comment text"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment on review {self.review_id} by {self.author.username}"
    
    def save(self, *args, **kwargs):
        """
        Custom save method with business logic validation:
        Only service owners and moderators can comment on reviews
        """
        # Ensure author is either the service owner or a moderator
        is_service_owner = (self.author == self.review.service.business)
        is_moderator = self.author.is_moderator
        
        if not (is_service_owner or is_moderator):
            raise ValueError("Only service owners and moderators can comment on reviews")
            
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['created_at']


class BlogCategory(models.Model):
    """
    Categories for blog posts and educational content
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogPost(models.Model):
    """
    Blog posts for educational content and information sharing.
    Can be created by any user.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    content = models.TextField()
    summary = models.TextField(blank=True, help_text="Short summary of the blog post")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blog_posts'
    )
    category = models.ForeignKey(
        BlogCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='blog_posts'
    )
    image = models.ImageField(
        upload_to='blog_images/', 
        null=True, 
        blank=True,
        help_text="Featured image for the blog post"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    views = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Resize the blog image on save if present and changed
        """
        if self.image:
            if not self.pk or (BlogPost.objects.filter(pk=self.pk).exists() and 
                               BlogPost.objects.get(pk=self.pk).image != self.image):
                self.image = resize_image(self.image, size=(1200, 800))
        
        super().save(*args, **kwargs)
        
    def increment_views(self):
        """
        Increment the view count for this blog post
        """
        self.views += 1
        self.save(update_fields=['views'])


class BlogComment(models.Model):
    """
    Comments on blog posts from any user
    """
    blog_post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='blog_comments'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment on '{self.blog_post.title}' by {self.author.username}"


class PaymentRequest(models.Model):
    """
    Model for payment requests from businesses to customers within an inquiry.
    
    Payment requests are created by business users and directed to customers.
    Customers can accept (triggers a transfer) or decline the request.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        DECLINED = 'DECLINED', _('Declined')
        
    request_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name='payment_requests'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_payment_requests',
        limit_choices_to={'role': User.Role.BUSINESS}
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_payment_requests',
        limit_choices_to={'role': User.Role.CUSTOMER}
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, help_text="Description of what this payment is for")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction = models.ForeignKey(
        Transaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='payment_request'
    )
    
    def __str__(self):
        return f"Payment request {self.request_id} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Validate that creator is business and recipient is customer
        if not self.creator.is_business:
            raise ValueError("Only business users can create payment requests")
        
        if self.recipient.role != User.Role.CUSTOMER:
            raise ValueError("Payment requests can only be sent to customers")
        
        # Ensure the creator is the business that owns the service in the inquiry
        if self.inquiry.service.business != self.creator:
            raise ValueError("You can only create payment requests for your own services")
        
        # Ensure the recipient is the customer who created the inquiry
        if self.inquiry.customer != self.recipient:
            raise ValueError("Payment requests must be sent to the customer who created the inquiry")
        
        super().save(*args, **kwargs)
    
    def accept(self):
        """
        Accept the payment request, transferring funds from recipient to creator.
        Creates a transaction record and updates the payment request status.
        """
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending payment requests can be accepted")
            
        recipient_wallet = self.recipient.wallet
        creator_wallet = self.creator.wallet
        
        try:
            # Transfer the funds
            transaction = recipient_wallet.transfer(creator_wallet, self.amount)
            
            # Update payment request
            self.status = self.Status.ACCEPTED
            self.transaction = transaction
            self.save(update_fields=['status', 'transaction', 'updated_at'])
            
            return transaction
        except ValueError as e:
            # Re-raise the error with a more descriptive message
            raise ValueError(f"Payment failed: {str(e)}")
    
    def decline(self):
        """
        Decline the payment request.
        """
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending payment requests can be declined")
            
        self.status = self.Status.DECLINED
        self.save(update_fields=['status', 'updated_at'])
        
        # No need to keep declined requests for long, they can be deleted after a certain period
        # For now, we just mark them as declined
        return True

