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
        # Function to ensure a user has a wallet
        def ensure_wallet(user):
            if not hasattr(user, 'wallet') or user.wallet is None:
                from django.apps import apps
                Wallet = apps.get_model('accounts', 'Wallet')
                wallet, created = Wallet.objects.get_or_create(user=user)
                return wallet
            return user.wallet
        
        # Create admin user
        try:
            admin = User.objects.filter(email='admin@test.com').first()
            if admin:
                print(f'Admin already exists: {admin.email}')
                admin.username = 'admin'
                admin.is_staff = True
                admin.is_superuser = True
                admin.role = User.Role.MODERATOR
                admin.set_password('admin123')
                admin.save()
            else:
                admin = User.objects.create_superuser(
                    username='admin',
                    email='admin@test.com',
                    password='admin123'
                )
                print(f'Created admin: {admin.email}')
            
            # Ensure wallet and set balance
            wallet = ensure_wallet(admin)
            wallet.balance = Decimal('100.00')
            wallet.save()
        except Exception as e:
            print(f'Error with admin user: {e}')
        
        # Create customer user
        try:
            customer = User.objects.filter(email='customer@test.com').first()
            if customer:
                print(f'Customer already exists: {customer.email}')
                customer.username = 'customer'
                customer.role = User.Role.CUSTOMER
                customer.set_password('customer123')
                customer.save()
            else:
                customer = User.objects.create_user(
                    username='customer',
                    email='customer@test.com',
                    password='customer123',
                    role=User.Role.CUSTOMER
                )
                print(f'Created customer: {customer.email}')
            
            # Ensure wallet and set balance
            wallet = ensure_wallet(customer)
            wallet.balance = Decimal('100.00')
            wallet.save()
        except Exception as e:
            print(f'Error with customer user: {e}')
        
        # Create moderator user
        try:
            moderator = User.objects.filter(email='moderator@test.com').first()
            if moderator:
                print(f'Moderator already exists: {moderator.email}')
                moderator.username = 'moderator'
                moderator.role = User.Role.MODERATOR
                moderator.set_password('moderator123')
                moderator.save()
            else:
                moderator = User.objects.create_user(
                    username='moderator',
                    email='moderator@test.com',
                    password='moderator123',
                    role=User.Role.MODERATOR
                )
                print(f'Created moderator: {moderator.email}')
            
            # Ensure wallet and set balance
            wallet = ensure_wallet(moderator)
            wallet.balance = Decimal('100.00')
            wallet.save()
        except Exception as e:
            print(f'Error with moderator user: {e}')
        
        # Create business user
        try:
            business = User.objects.filter(email='business@test.com').first()
            if business:
                print(f'Business already exists: {business.email}')
                business.username = 'business'
                business.role = User.Role.BUSINESS
                business.set_password('business123')
                business.save()
            else:
                business = User.objects.create_user(
                    username='business',
                    email='business@test.com',
                    password='business123',
                    role=User.Role.BUSINESS
                )
                print(f'Created business: {business.email}')
            
            # Ensure wallet and set balance
            wallet = ensure_wallet(business)
            wallet.balance = Decimal('100.00')
            wallet.save()
        except Exception as e:
            print(f'Error with business user: {e}')

if __name__ == "__main__":
    create_test_users()