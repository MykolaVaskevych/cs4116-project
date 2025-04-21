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

# Create test users first if requested
if [ "${CREATE_TEST_USERS:-false}" = "true" ]; then
    echo "Creating test users (admin, customer, moderator, business)..."
    python create_test_users.py
fi

# Skip creating superuser if we already created test users
if [ "${CREATE_TEST_USERS:-false}" != "true" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating admin superuser..."
    # Use a more reliable approach with echo for Railway
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME:-admin}', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD') if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists() else None" | python manage.py shell
    
    # Verify superuser was created
    echo "Admin user creation completed."
fi

# Reset database if requested
if [ "${RESET_DATABASE:-false}" = "true" ]; then
    echo "Resetting database..."
    python manage.py flush --no-input
fi

# Generate demo data if requested
if [ "${GENERATE_DEMO_DATA:-false}" = "true" ]; then
    echo "Generating demo data for the application..."
    python generate_demo_data.py
fi

# Execute the command passed to the script
exec "$@"