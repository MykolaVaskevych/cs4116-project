from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.contrib.auth.hashers import make_password
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
            from .models import Wallet  # Import here to avoid circular import
            Wallet.objects.create(user=user)
            
        return user
    
    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email for authentication
    """
    # Override email field to make it unique and required
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        },
    )
    
    # Use our custom manager that handles wallet creation
    objects = UserManager()
    
    # Make email the username field for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Still required for admin creation
    
    def __str__(self):
        return self.email


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
            
        self.balance += amount
        self.save(update_fields=['balance', 'updated_at'])
        
        # Create transaction record directly
        return Transaction.objects.create(
            to_wallet=self,
            amount=amount,
            transaction_type=Transaction.TransactionType.DEPOSIT
        )
        
    def withdraw(self, amount):
        """Withdraw funds from wallet and create transaction record"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        if self.balance < amount:
            raise ValueError("Insufficient funds")
            
        self.balance -= amount
        self.save(update_fields=['balance', 'updated_at'])
        
        # Create transaction record
        return Transaction.objects.create(
            from_wallet=self,
            amount=amount,
            transaction_type=Transaction.TransactionType.WITHDRAWAL
        )
        
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