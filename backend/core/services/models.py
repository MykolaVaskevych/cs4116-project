from django.db import models
from django.utils import timezone
from accounts.models import User

SERVICE_STATUS = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class Category(models.Model):
    """Categories for organizing services"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For UI icons (CSS class names)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """Service listings offered by providers"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    location = models.CharField(max_length=200, blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=SERVICE_STATUS, default='pending')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.provider.username}"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)


class Review(models.Model):
    """Reviews for services"""
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1-5 star rating

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('service', 'user')  # One review per service per user
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s review of {self.service.title}"


BOOKING_STATUS = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

class Booking(models.Model):
    """Booking requests / appointments for services"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-schedule_date']

    def __str__(self):
        return f"Booking for {self.service.title} by {self.customer.username}"
