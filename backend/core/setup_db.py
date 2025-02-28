#!/usr/bin/env python
"""
Database setup script for Urban Life Hub project.
This script:
1. Creates the MySQL database if it doesn't exist
2. Runs migrations to set up tables
3. Creates initial categories and other base data
4. Creates a superuser if desired
"""
import os
import sys
import argparse
import MySQLdb
import django
from django.db import connection
from django.core.management import call_command

# Get the current file's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure that the parent directory is in Python's path for imports
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Setup Django settings if in backend/core directory
if os.path.basename(SCRIPT_DIR) == 'core':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    # Setup Django - this will load settings
    django.setup()
else:
    print("This script should be run from the 'backend/core' directory.")
    sys.exit(1)

# Import settings after Django setup
from django.conf import settings


def create_database(db_settings):
    """
    Create the MySQL database if it doesn't exist.
    """
    try:
        print(f"Attempting to create database '{db_settings['NAME']}' if it doesn't exist...")
        
        # Connect to MySQL server (without selecting a database)
        conn = MySQLdb.connect(
            host=db_settings.get('HOST', '127.0.0.1'),
            user=db_settings.get('USER', 'root'),
            passwd=db_settings.get('PASSWORD', ''),
            port=int(db_settings.get('PORT', 3306))
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_settings['NAME']} "
                      f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        
        print(f"Database '{db_settings['NAME']}' created or already exists.")
        
        # Close the connection
        cursor.close()
        conn.close()
        return True
        
    except MySQLdb.Error as e:
        print(f"Error creating database: {e}")
        return False


def apply_migrations():
    """
    Apply Django migrations to create tables.
    """
    print("Applying migrations...")
    try:
        call_command('makemigrations', 'accounts', 'services', 'messaging', 'resources')
        call_command('migrate')
        print("Migrations applied successfully.")
        return True
    except Exception as e:
        print(f"Error applying migrations: {e}")
        return False


def create_initial_data():
    """
    Create initial data for the application.
    This includes categories and any other base data needed.
    """
    print("Creating initial data...")
    try:
        # Import our models
        from services.models import Category
        
        # Create categories if they don't exist
        categories = [
            "Legal & Finance",
            "Health & Wellness",
            "Home & Lifestyle",
            "Technology",
            "Education & Career",
            "Personal Development"
        ]
        
        for category_name in categories:
            Category.objects.get_or_create(name=category_name)
            
        print(f"Created {len(categories)} categories.")
        return True
    except Exception as e:
        print(f"Error creating initial data: {e}")
        return False


def create_superuser(username, email, password):
    """
    Create a superuser if it doesn't exist.
    """
    from accounts.models import User
    
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
        return True
    
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")
        return True
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return False


def main():
    """
    Main function to run the setup process.
    """
    parser = argparse.ArgumentParser(description='Set up the Urban Life Hub database.')
    parser.add_argument('--superuser', action='store_true', 
                        help='Create a superuser after setup')
    parser.add_argument('--username', default='admin',
                        help='Superuser username (default: admin)')
    parser.add_argument('--email', default='admin@example.com',
                        help='Superuser email (default: admin@example.com)')
    parser.add_argument('--password', default='adminpassword',
                        help='Superuser password (default: adminpassword)')
    
    args = parser.parse_args()
    
    print("Starting Urban Life Hub database setup...")
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    # Create the database
    if not create_database(db_settings):
        print("Failed to create database. Exiting.")
        return
    
    # Apply migrations
    if not apply_migrations():
        print("Failed to apply migrations. Exiting.")
        return
    
    # Create initial data
    if not create_initial_data():
        print("Failed to create initial data. Continuing anyway...")
    
    # Create superuser if requested
    if args.superuser:
        if not create_superuser(args.username, args.email, args.password):
            print("Failed to create superuser. Setup otherwise complete.")
        else:
            print(f"Superuser created with username: {args.username}, password: {args.password}")
    
    print("Urban Life Hub database setup complete!")


if __name__ == "__main__":
    main()