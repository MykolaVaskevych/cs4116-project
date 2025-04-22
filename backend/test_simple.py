from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounts.models import Service, Category, Inquiry, Wallet, Transaction
from accounts.serializers import InquiryCreateSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction as db_transaction

User = get_user_model()

def run_test():
    print("Creating test users...")
    
    try:
        business_user = User.objects.get(email="business@example.com")
    except User.DoesNotExist:
        business_user = User.objects.create_user(
            username="testbusiness",
            email="business@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
    
    try:
        customer_user = User.objects.get(email="customer@example.com")
    except User.DoesNotExist:
        customer_user = User.objects.create_user(
            username="testcustomer",
            email="customer@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
    
    print("Adding funds to customer wallet...")
    customer_user.wallet.deposit(Decimal("100.00"))
    
    print("Creating test services...")
    category, created = Category.objects.get_or_create(name="Test Category")
    
    paid_service, created = Service.objects.get_or_create(
        name="Paid Service",
        defaults={
            "description": "This is a paid service",
            "fixed_price": Decimal("10.00"),
            "business": business_user,
            "category": category
        }
    )
    
    free_service, created = Service.objects.get_or_create(
        name="Free Service",
        defaults={
            "description": "This is a free service",
            "fixed_price": Decimal("0.00"),
            "business": business_user,
            "category": category
        }
    )
    
    # Test paid service inquiry
    print("\nTesting paid service inquiry...")
    customer_initial_balance = customer_user.wallet.balance
    business_initial_balance = business_user.wallet.balance
    
    print(f"Initial balances - Customer: {customer_initial_balance}, Business: {business_initial_balance}")
    
    context = {'request': type('obj', (object,), {'user': customer_user})}
    data = {
        'service': paid_service.id,
        'subject': 'Test Paid Inquiry',
        'initial_message': 'This is a test message for a paid service'
    }
    
    serializer = InquiryCreateSerializer(data=data, context=context)
    if serializer.is_valid():
        inquiry = serializer.save()
        print("Inquiry created successfully")
        
        customer_user.wallet.refresh_from_db()
        business_user.wallet.refresh_from_db()
        
        print(f"Final balances - Customer: {customer_user.wallet.balance}, Business: {business_user.wallet.balance}")
        
        messages = inquiry.messages.all()
        print(f"Number of messages: {messages.count()}")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.content}")
    else:
        print("Serializer validation failed:")
        print(serializer.errors)
    
    # Test free service inquiry
    print("\nTesting free service inquiry...")
    context = {'request': type('obj', (object,), {'user': customer_user})}
    data = {
        'service': free_service.id,
        'subject': 'Test Free Inquiry',
        'initial_message': 'This is a test message for a free service'
    }
    
    serializer = InquiryCreateSerializer(data=data, context=context)
    if serializer.is_valid():
        inquiry = serializer.save()
        print("Inquiry created successfully")
        
        messages = inquiry.messages.all()
        print(f"Number of messages: {messages.count()}")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.content}")
    else:
        print("Serializer validation failed:")
        print(serializer.errors)

run_test()
