from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Roles can be: 'customer', 'pending_provider', 'provider', or 'moderator'.
    """
    role = models.CharField(max_length=50, default='customer')
    business_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def can_buy(self):
        """
        Returns True if this user can purchase (customer or provider),
        but not moderators.
        """
        return self.role in ['customer', 'provider']

    @property
    def can_sell(self):
        """
        Returns True if this user can create services (provider).
        """
        return self.role == 'provider'

    @property
    def is_provider(self):
        return self.role == 'provider'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @property
    def is_customer(self):
        return self.role == 'customer'


class Wallet(models.Model):
    """
    Wallet model to store user balances.
    One-to-one with User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username}'s wallet (${self.balance})"
