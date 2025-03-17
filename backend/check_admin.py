#!/usr/bin/env python
"""
Script to force creation of admin user with proper login credentials
"""
import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Admin credentials
username = 'admin'
email = 'admin@example.com'  # LOGIN FIELD - use this to log in
password = 'UrbanLife2025!'

# Force recreation regardless of whether user exists
with transaction.atomic():
    # Delete any existing admin users with this email to avoid conflicts
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"Removing existing admin user: {email}")
        user.delete()
    
    # Create a completely fresh superuser
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    
    # Make sure it has admin rights
    user.is_staff = True
    user.is_superuser = True
    user.role = User.Role.MODERATOR
    user.save()
    
    print(f"\n✅ ADMIN USER CREATED SUCCESSFULLY")
    print(f"------------------------------")
    print(f"Email: {email}")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Is staff: {user.is_staff}")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Role: {user.role}")

print("\n🔴 IMPORTANT: LOG IN WITH EMAIL NOT USERNAME 🔴")
print(f"Email: {email}")
print(f"Password: {password}")
print("Login URL: /admin/")