#!/usr/bin/env python
"""
Script to check and create admin user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Default credentials (same as in railway.toml)
username = 'admin'
email = 'admin@example.com'
password = 'UrbanLife2025!'

# Check if user exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"Admin user exists: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Is staff: {user.is_staff}")
    # Reset password
    user.set_password(password)
    user.save()
    print(f"Password has been reset to: {password}")
else:
    # Create user
    user = User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Created new admin user: {username}")
    print(f"Password: {password}")

print("\nTry logging in with these credentials at /admin/")