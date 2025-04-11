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
        # Create admin user
        try:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='admin123'
            )
            admin.wallet.balance = Decimal('100.00')
            admin.wallet.save()
            print(f'Created admin: {admin.email}')
        except Exception as e:
            print(f'Error creating admin: {e}')
        
        # Create customer user
        try:
            customer = User.objects.create_user(
                username='customer',
                email='customer@test.com',
                password='customer123',
                role=User.Role.CUSTOMER
            )
            customer.wallet.balance = Decimal('100.00')
            customer.wallet.save()
            print(f'Created customer: {customer.email}')
        except Exception as e:
            print(f'Error creating customer: {e}')
        
        # Create moderator user
        try:
            moderator = User.objects.create_user(
                username='moderator',
                email='moderator@test.com',
                password='moderator123',
                role=User.Role.MODERATOR
            )
            moderator.wallet.balance = Decimal('100.00')
            moderator.wallet.save()
            print(f'Created moderator: {moderator.email}')
        except Exception as e:
            print(f'Error creating moderator: {e}')
        
        # Create business user
        try:
            business = User.objects.create_user(
                username='business',
                email='business@test.com',
                password='business123',
                role=User.Role.BUSINESS
            )
            business.wallet.balance = Decimal('100.00')
            business.wallet.save()
            print(f'Created business: {business.email}')
        except Exception as e:
            print(f'Error creating business: {e}')

if __name__ == "__main__":
    create_test_users()