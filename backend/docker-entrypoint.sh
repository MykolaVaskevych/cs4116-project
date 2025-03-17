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

# Create superuser
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput || echo "Superuser already exists."
fi

# Execute the command passed to the script
exec "$@"