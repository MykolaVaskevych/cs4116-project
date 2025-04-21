from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from accounts.models import Service, Category, Inquiry, Wallet, Transaction
from accounts.serializers import InquiryCreateSerializer
from rest_framework.exceptions import ValidationError
from django.db import transaction as db_transaction

User = get_user_model()

# Create test data
def setup_test_data():
    # Create test users
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
    
    # Add funds to customer wallet
    customer_user.wallet.deposit(Decimal("100.00"))
    
    # Create category
    category, created = Category.objects.get_or_create(name="Test Category")
    
    # Get or create paid service
    paid_service, created = Service.objects.get_or_create(
        name="Paid Service",
        defaults={
            "description": "This is a paid service",
            "fixed_price": Decimal("10.00"),
            "business": business_user,
            "category": category
        }
    )
    
    # Get or create free service
    free_service, created = Service.objects.get_or_create(
        name="Free Service",
        defaults={
            "description": "This is a free service",
            "fixed_price": Decimal("0.00"),
            "business": business_user,
            "category": category
        }
    )
    
    return {
        'business_user': business_user,
        'customer_user': customer_user,
        'paid_service': paid_service,
        'free_service': free_service
    }

# Test inquiry creation with paid service
def test_paid_service_inquiry():
    test_data = setup_test_data()
    
    # Test data
    customer = test_data['customer_user']
    paid_service = test_data['paid_service']
    business = test_data['business_user']
    
    # Initial balances
    customer_initial_balance = customer.wallet.balance
    business_initial_balance = business.wallet.balance
    
    # Create inquiry using serializer
    context = {'request': type('obj', (object,), {'user': customer})}
    data = {
        'service': paid_service.id,
        'subject': 'Test Inquiry',
        'initial_message': 'This is a test message'
    }
    
    serializer = InquiryCreateSerializer(data=data, context=context)
    if serializer.is_valid():
        inquiry = serializer.save()
        print("✅ Inquiry created successfully")
        
        # Check balances after transaction
        customer.wallet.refresh_from_db()
        business.wallet.refresh_from_db()
        customer_final_balance = customer.wallet.balance
        business_final_balance = business.wallet.balance
        
        print(f"Customer initial balance: {customer_initial_balance}")
        print(f"Customer final balance: {customer_final_balance}")
        print(f"Business initial balance: {business_initial_balance}")
        print(f"Business final balance: {business_final_balance}")
        
        # Verify payment was processed
        paid_amount = paid_service.fixed_price
        print(f"Expected payment: {paid_amount}")
        
        if customer_final_balance == customer_initial_balance - paid_amount:
            print("✅ Customer balance correctly reduced")
        else:
            print("❌ Customer balance not correctly updated")
            
        if business_final_balance == business_initial_balance + paid_amount:
            print("✅ Business balance correctly increased")
        else:
            print("❌ Business balance not correctly updated")
        
        # Check inquiry messages
        messages = inquiry.messages.all()
        print(f"Number of messages: {messages.count()}")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.content}")
    else:
        print("❌ Serializer validation failed:")
        print(serializer.errors)

# Test inquiry creation with free service
def test_free_service_inquiry():
    test_data = setup_test_data()
    
    # Test data
    customer = test_data['customer_user']
    free_service = test_data['free_service']
    
    # Create inquiry using serializer
    context = {'request': type('obj', (object,), {'user': customer})}
    data = {
        'service': free_service.id,
        'subject': 'Test Free Inquiry',
        'initial_message': 'This is a test message for a free service'
    }
    
    serializer = InquiryCreateSerializer(data=data, context=context)
    if serializer.is_valid():
        inquiry = serializer.save()
        print("✅ Free inquiry created successfully")
        
        # Check inquiry messages
        messages = inquiry.messages.all()
        print(f"Number of messages: {messages.count()}")
        for i, msg in enumerate(messages):
            print(f"Message {i+1}: {msg.content}")
    else:
        print("❌ Serializer validation failed for free service:")
        print(serializer.errors)

# Run the tests
print("TESTING PAID SERVICE INQUIRY:")
try:
    with db_transaction.atomic():
        test_paid_service_inquiry()
        # Rollback the transaction to avoid creating real records
        raise Exception("Rolling back test transaction")
except Exception as e:
    if str(e) \!= "Rolling back test transaction":
        print(f"❌ Test failed with error: {e}")

print("\nTESTING FREE SERVICE INQUIRY:")
try:
    with db_transaction.atomic():
        test_free_service_inquiry()
        # Rollback the transaction to avoid creating real records
        raise Exception("Rolling back test transaction")
except Exception as e:
    if str(e) \!= "Rolling back test transaction":
        print(f"❌ Test failed with error: {e}")
