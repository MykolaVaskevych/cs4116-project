from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.contrib.auth.hashers import make_password
from django.db.models import DO_NOTHING
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid

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


class Service(models.Model):
    """Model for business services that can be offered to customers"""
    
    name = models.CharField(max_length=100)
    description = models.TextField()
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
        null=True
    )
    subject = models.CharField(max_length=100)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN
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
    """Model for reviews based on a service"""

    #each review has an id that is automatically incremented
    review_id = models.AutoField(primary_key=True)
    #if service is deleted its reviews will be also
    service_id = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
    )
    #dont delete review even if user was deleted
    user_id = models.ForeignKey(
        User,
        related_name='reviews',
        on_delete=DO_NOTHING
    )
    #reviews can be rated 0-5 stars
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    #comments can be added optionally if the user wants
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Enforce inquiry status check before saving"""
        inquiry = Inquiry.objects.filter(user=self.user_id, service=self.service_id).first()

        if not inquiry or inquiry.status != Inquiry.Status.CLOSED:
            raise ValueError("You can only leave an inquiry review if it's status is closed")

        super().save(*args, **kwargs)

