#!/bin/bash
set -e

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create media directory if it doesn't exist
echo "Setting up media directory..."
mkdir -p media/profile_images
mkdir -p media/service_logos
chmod -R 755 media

# Always collect static files in production environment
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser (using custom script for more reliability)
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating admin superuser..."
    
    # Create a temporary script to ensure admin user creation
    cat > /tmp/create_admin.py << 'EOF'
import os
import django
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Get credentials from environment
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'UrbanLife2025!')

print(f"Creating/updating admin user: {email}")

with transaction.atomic():
    # Delete any existing admin user with this email to avoid conflicts
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"Removing existing admin user: {email}")
        user.delete()
    
    # Create a fresh superuser
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    
    # Explicitly set all admin flags
    user.is_staff = True
    user.is_superuser = True
    user.role = User.Role.MODERATOR
    user.save()
    
    print(f"✅ Admin user created successfully:")
    print(f"  Email: {email}")
    print(f"  Username: {username}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Is superuser: {user.is_superuser}")
    print(f"  Role: {user.role}")
    print(f"\n🔴 IMPORTANT: LOG IN WITH EMAIL NOT USERNAME 🔴")
EOF

    # Run the script
    python /tmp/create_admin.py
    
    # Remove the temporary script
    rm /tmp/create_admin.py
fi

# Execute the command passed to the script
exec "$@"