from django.db import models
from django.utils import timezone
from accounts.models import User
from services.models import Category


class ResourceCategory(models.Model):
    """Categories for organizing educational resources"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For UI icons (CSS class names)
    related_service_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, 
                                               related_name='resource_categories')
    
    class Meta:
        verbose_name_plural = "Resource Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Resource(models.Model):
    """Educational resources for the Adulting 101 section"""
    TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('checklist', 'Checklist'),
        ('template', 'Template'),
        ('guide', 'Step-by-Step Guide')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='article')
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_resources')
    is_featured = models.BooleanField(default=False)
    external_url = models.URLField(blank=True, null=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)  # URL to image
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class ResourceSave(models.Model):
    """Tracks when users save resources for later viewing"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='saves')
    saved_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'resource')
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} saved '{self.resource.title}'"


class Comment(models.Model):
    """User comments on resources"""
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.resource.title}"