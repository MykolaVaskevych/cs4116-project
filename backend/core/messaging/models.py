from django.db import models
from django.utils import timezone
from accounts.models import User
from services.models import Service, Booking


class Conversation(models.Model):
    """Thread of messages between users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()])
        return f"Conversation between {participant_names}"
    
    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    """Individual messages in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Transaction(models.Model):
    """Payment transactions between users"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='transaction')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earnings')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, unique=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transaction {self.reference}: ${self.amount} from {self.customer.username} to {self.provider.username}"


class Notification(models.Model):
    """System notifications for users"""
    TYPE_CHOICES = [
        ('message', 'New Message'),
        ('booking', 'Booking Update'),
        ('payment', 'Payment Update'),
        ('review', 'New Review'),
        ('system', 'System Notice')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    related_booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)
    related_conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.type} notification for {self.user.username}: {self.title}"