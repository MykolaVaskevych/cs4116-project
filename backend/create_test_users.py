#!/usr/bin/env python
import os
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import models
from accounts.models import User
from django.db import transaction

def create_test_users():
    """Create test users with standard credentials"""
    
    with transaction.atomic():
        # Create or get admin user
        admin, created = User.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'username': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'role': User.Role.MODERATOR
            }
        )
        
        if created:
            admin.set_password('admin123')
            admin.save()
            admin.wallet.balance = Decimal('100.00')
            admin.wallet.save()
            print(f'Created admin: {admin.email}')
        else:
            print(f'Admin already exists: {admin.email}')
            # Ensure the password is set correctly
            admin.set_password('admin123')
            admin.save()
        
        # Create or get customer user
        customer, created = User.objects.get_or_create(
            email='customer@test.com',
            defaults={
                'username': 'customer',
                'role': User.Role.CUSTOMER
            }
        )
        
        if created:
            customer.set_password('customer123')
            customer.save()
            customer.wallet.balance = Decimal('100.00')
            customer.wallet.save()
            print(f'Created customer: {customer.email}')
        else:
            print(f'Customer already exists: {customer.email}')
            # Ensure the password is set correctly
            customer.set_password('customer123')
            customer.save()
        
        # Create or get moderator user
        moderator, created = User.objects.get_or_create(
            email='moderator@test.com',
            defaults={
                'username': 'moderator',
                'role': User.Role.MODERATOR
            }
        )
        
        if created:
            moderator.set_password('moderator123')
            moderator.save()
            moderator.wallet.balance = Decimal('100.00')
            moderator.wallet.save()
            print(f'Created moderator: {moderator.email}')
        else:
            print(f'Moderator already exists: {moderator.email}')
            # Ensure the password is set correctly
            moderator.set_password('moderator123')
            moderator.save()
        
        # Create or get business user
        business, created = User.objects.get_or_create(
            email='business@test.com',
            defaults={
                'username': 'business',
                'role': User.Role.BUSINESS
            }
        )
        
        if created:
            business.set_password('business123')
            business.save()
            business.wallet.balance = Decimal('100.00')
            business.wallet.save()
            print(f'Created business: {business.email}')
        else:
            print(f'Business already exists: {business.email}')
            # Ensure the password is set correctly
            business.set_password('business123')
            business.save()

if __name__ == "__main__":
    create_test_users()