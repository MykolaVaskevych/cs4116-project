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
email = 'admin@example.com'  # This is the login field
password = 'UrbanLife2025!'

# Check if user exists by email (since email is the USERNAME_FIELD)
if User.objects.filter(email=email).exists():
    user = User.objects.get(email=email)
    print(f"Admin user exists with email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Is superuser: {user.is_superuser}")
    print(f"Is staff: {user.is_staff}")
    # Reset password
    user.set_password(password)
    user.save()
    print(f"Password has been reset to: {password}")
else:
    # Create user - note the order of parameters (email is the USERNAME_FIELD)
    user = User.objects.create_superuser(email=email, username=username, password=password)
    print(f"Created new admin user with:")
    print(f"Email: {email} (use this to log in)")
    print(f"Username: {username}")
    print(f"Password: {password}")

print("\n*** IMPORTANT: LOG IN WITH EMAIL NOT USERNAME ***")
print(f"Email: {email}")
print(f"Password: {password}")
print("Login URL: /admin/")