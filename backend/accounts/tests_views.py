from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import (
    User, Wallet, Transaction, Category, Service, 
    Inquiry, InquiryMessage, Review, ReviewComment
)

User = get_user_model()

class ViewsTestCase(APITestCase):
    def setUp(self):
        # Create users with different roles
        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        self.business = User.objects.create_user(
            username="business",
            email="business@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        self.moderator = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="password123",
            role=User.Role.MODERATOR
        )
        
        # Create a second customer for testing
        self.customer2 = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        # Create a second business for testing
        self.business2 = User.objects.create_user(
            username="business2",
            email="business2@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        # Create a second moderator for testing
        self.moderator2 = User.objects.create_user(
            username="moderator2",
            email="moderator2@example.com",
            password="password123",
            role=User.Role.MODERATOR
        )
        
        # Set up API clients
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
        self.customer2_client = APIClient()
        self.customer2_client.force_authenticate(user=self.customer2)
        
        self.business2_client = APIClient()
        self.business2_client.force_authenticate(user=self.business2)
        
        # Create category
        self.category = Category.objects.create(
            name="Cleaning",
            description="Cleaning services"
        )
        
        # Create service
        self.service = Service.objects.create(
            name="Home Cleaning",
            description="Professional home cleaning service",
            business=self.business,
            category=self.category
        )
        
        # Create service for business2
        self.service2 = Service.objects.create(
            name="Office Cleaning",
            description="Professional office cleaning service",
            business=self.business2,
            category=self.category
        )

    def test_register_login_endpoints(self):
        """Test user registration and login"""
        # Register endpoint
        register_url = reverse('accounts:register')
        
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Role.CUSTOMER
        }
        
        response = self.client.post(register_url, register_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Login endpoint
        login_url = reverse('accounts:login')
        
        login_data = {
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        
        # Invalid login
        invalid_login = {
            'email': 'newuser@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(login_url, invalid_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_profile_endpoints(self):
        """Test user profile endpoints"""
        profile_url = reverse('accounts:profile')
        
        # Get profile
        response = self.customer_client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.customer.email)
        
        # Update profile (PATCH)
        update_data = {
            'first_name': 'Updated',
            'bio': 'This is my updated bio'
        }
        
        response = self.customer_client.patch(profile_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['bio'], 'This is my updated bio')
        
        # Update profile (PUT - full update)
        full_update_data = {
            'first_name': 'Fully',
            'last_name': 'Updated',
            'username': 'customer',  # Keep the same to avoid unique constraint
            'email': 'customer@example.com',  # Keep the same to avoid unique constraint
            'bio': 'Complete profile update'
        }
        
        response = self.customer_client.put(profile_url, full_update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Fully')
        self.assertEqual(response.data['last_name'], 'Updated')
        self.assertEqual(response.data['bio'], 'Complete profile update')
    
    def test_wallet_endpoints(self):
        """Test wallet related endpoints"""
        # Get wallet details
        wallet_url = reverse('accounts:wallet')
        response = self.customer_client.get(wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), Decimal('0.00'))
        
        # Deposit to wallet
        deposit_url = reverse('accounts:deposit')
        deposit_data = {'amount': '100.00'}
        
        response = self.customer_client.post(deposit_url, deposit_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], '100.00')
        
        # Withdraw from wallet
        withdraw_url = reverse('accounts:withdraw')
        withdraw_data = {'amount': '50.00'}
        
        response = self.customer_client.post(withdraw_url, withdraw_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], '50.00')
        
        # Withdraw too much (should fail)
        withdraw_too_much = {'amount': '200.00'}
        response = self.customer_client.post(withdraw_url, withdraw_too_much, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Transfer to another wallet
        transfer_url = reverse('accounts:transfer')
        transfer_data = {
            'amount': '25.00',
            'recipient_email': self.business.email
        }
        
        response = self.customer_client.post(transfer_url, transfer_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], '25.00')
        
        # Transfer to non-existent user
        invalid_transfer = {
            'amount': '10.00',
            'recipient_email': 'nonexistent@example.com'
        }
        
        response = self.customer_client.post(transfer_url, invalid_transfer, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # List transactions
        transaction_url = reverse('accounts:transactions')
        response = self.customer_client.get(transaction_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)  # At least one transaction
    
    def test_category_viewset(self):
        """Test category viewset endpoints"""
        # List categories
        categories_url = '/api/categories/'
        response = self.customer_client.get(categories_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Get category detail
        category_detail_url = f'/api/categories/{self.category.id}/'
        response = self.customer_client.get(category_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Cleaning')
        
        # Create category (only moderator can do this)
        new_category_data = {
            'name': 'Gardening',
            'description': 'Gardening services'
        }
        
        # Try with customer (should fail)
        response = self.customer_client.post(categories_url, new_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with moderator (should succeed)
        response = self.moderator_client.post(categories_url, new_category_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Gardening')
        
        # Update category (only moderator can do this)
        update_data = {'description': 'Updated gardening services'}
        gardening_id = response.data['id']
        gardening_url = f'/api/categories/{gardening_id}/'
        
        # Try with customer (should fail)
        response = self.customer_client.patch(gardening_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with moderator (should succeed)
        response = self.moderator_client.patch(gardening_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated gardening services')
        
        # Delete category (only moderator can do this)
        # Try with customer (should fail)
        response = self.customer_client.delete(gardening_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with moderator (should succeed)
        response = self.moderator_client.delete(gardening_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_service_viewset(self):
        """Test service viewset endpoints"""
        # List services
        services_url = '/api/services/'
        response = self.customer_client.get(services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Get service detail
        service_detail_url = f'/api/services/{self.service.id}/'
        response = self.customer_client.get(service_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Home Cleaning')
        
        # Create service (only business can do this)
        new_service_data = {
            'name': 'Window Cleaning',
            'description': 'Professional window cleaning service',
            'category': self.category.id
        }
        
        # Try with customer (should fail)
        response = self.customer_client.post(services_url, new_service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with business (should succeed)
        response = self.business_client.post(services_url, new_service_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Window Cleaning')
        
        # Get my services (filter for business)
        my_services_url = '/api/services/?my_services=true'
        response = self.business_client.get(my_services_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Original + new service
        
        # Update service (only owner can do this)
        update_data = {'description': 'Updated window cleaning service'}
        window_cleaning_id = response.data[0]['id']
        window_cleaning_url = f'/api/services/{window_cleaning_id}/'
        
        # Try with customer (should fail)
        response = self.customer_client.patch(window_cleaning_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with business owner (should succeed)
        response = self.business_client.patch(window_cleaning_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated window cleaning service')
        
        # Delete service (only owner can do this)
        # Try with customer (should fail)
        response = self.customer_client.delete(window_cleaning_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Try with business owner (should succeed)
        response = self.business_client.delete(window_cleaning_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_inquiry_workflow(self):
        """Test inquiry creation, messaging, and closing workflow"""
        # First verify inquiry endpoint exists
        inquiries_url = '/api/inquiries/'
        response = self.customer_client.get(inquiries_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create an inquiry directly through the model
        inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Question about cleaning"
        )
        
        # Create initial message
        initial_message = InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=self.customer,
            content="I would like to know more about your service"
        )
        
        # Get inquiry details
        inquiry_detail_url = f'/api/inquiries/{inquiry.id}/'
        response = self.customer_client.get(inquiry_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subject'], 'Question about cleaning')
        
        # List inquiries
        response = self.customer_client.get(inquiries_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
        # Business can also see the inquiry
        response = self.business_client.get(inquiries_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
        # Add message through model
        business_message = InquiryMessage.objects.create(
            inquiry=inquiry,
            sender=self.business,
            content="Yes, we can help with that"
        )
        
        # Close inquiry (only moderator can do this)
        close_url = f'/api/inquiries/{inquiry.id}/close/'
        
        # Try as customer (should fail)
        response = self.customer_client.post(close_url)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])
        
        # Close directly using model method
        inquiry.close(self.moderator)
        
        # Verify inquiry is closed
        response = self.customer_client.get(inquiry_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'CLOSED')
        
    def test_moderator_request_endpoints(self):
        """Test moderator request and list endpoints"""
        # Create an inquiry without a moderator
        inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Need moderator inquiry"
        )
        
        # List moderators
        moderator_list_url = reverse('accounts:moderator-list')
        response = self.customer_client.get(moderator_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # We have two moderators
        
        # Request a moderator
        moderator_request_url = reverse('accounts:moderator-request')
        request_data = {'inquiry_id': inquiry.id}
        
        # Customer can request a moderator
        response = self.customer_client.post(moderator_request_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update inquiry from database
        inquiry.refresh_from_db()
        
        # Inquiry should now have moderator request flag set and moderator assigned
        self.assertTrue(inquiry.has_moderator_request)
        self.assertIsNotNone(inquiry.moderator)
        
        # Can't request a moderator if one is already assigned
        response = self.customer_client.post(moderator_request_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Create another inquiry for testing
        inquiry2 = Inquiry.objects.create(
            service=self.service2,
            customer=self.customer2,
            subject="Another inquiry needing moderator"
        )
        
        # Business can also request moderator
        request_data = {'inquiry_id': inquiry2.id}
        response = self.business2_client.post(moderator_request_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Update inquiry from database
        inquiry2.refresh_from_db()
        self.assertTrue(inquiry2.has_moderator_request)
        self.assertIsNotNone(inquiry2.moderator)
        
        # User not involved in inquiry can't request moderator
        inquiry3 = Inquiry.objects.create(
            service=self.service,
            customer=self.customer2,
            subject="Third inquiry"
        )
        
        request_data = {'inquiry_id': inquiry3.id}
        # This business isn't involved in inquiry3
        response = self.business2_client.post(moderator_request_url, request_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_payment_request_workflow(self):
        """Test payment request creation, listing, and processing workflow"""
        # Create an open inquiry for payment testing
        inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Payment inquiry"
        )
        
        # Fund customer wallet for testing payment acceptance
        self.customer.wallet.deposit(Decimal('500.00'))
        
        # Create payment request
        payment_requests_url = reverse('accounts:payment-request-list-create')
        
        payment_data = {
            'inquiry': inquiry.id,
            'amount': '100.00',
            'description': 'Payment for cleaning services'
        }
        
        # Customer shouldn't be able to create payment requests
        response = self.customer_client.post(payment_requests_url, payment_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])
        
        # Business should be able to create payment requests
        response = self.business_client.post(payment_requests_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '100.00')
        
        payment_request_id = response.data['request_id']
        
        # Business can list their created payment requests
        response = self.business_client.get(payment_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Customer can see payment requests directed to them
        response = self.customer_client.get(payment_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Moderator can see all payment requests
        response = self.moderator_client.get(payment_requests_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # List pending payment requests
        pending_url = reverse('accounts:pending-payment-requests')
        response = self.customer_client.get(pending_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Get payment request details by ID
        detail_url = reverse('accounts:payment-request-detail', args=[payment_request_id])
        response = self.customer_client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'PENDING')
        
        # Accept payment request
        action_url = reverse('accounts:payment-request-action', args=[payment_request_id])
        action_data = {'action': 'accept'}
        
        # Only recipient can accept
        response = self.business_client.post(action_url, action_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Customer accepting payment
        response = self.customer_client.post(action_url, action_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('transaction_id', response.data)
        
        # Check that payment request status is updated
        response = self.customer_client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ACCEPTED')
        
        # Refresh objects from database to get updated wallet balances
        self.customer.refresh_from_db()
        self.business.refresh_from_db()
        
        # Check that customer balance is reduced
        wallet_url = reverse('accounts:wallet')
        response = self.customer_client.get(wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), Decimal('400.00'))
        
        # Check that business balance is increased
        response = self.business_client.get(wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), Decimal('100.00'))
        
        # Create another payment request to test declination
        inquiry2 = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Another payment inquiry"
        )
        
        payment_data = {
            'inquiry': inquiry2.id,
            'amount': '50.00',
            'description': 'Another payment request'
        }
        
        response = self.business_client.post(payment_requests_url, payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        payment_request_id2 = response.data['request_id']
        action_url2 = reverse('accounts:payment-request-action', args=[payment_request_id2])
        
        # Decline payment request
        decline_data = {'action': 'decline'}
        response = self.customer_client.post(action_url2, decline_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Payment request declined')
        
        # Check that request is marked as declined
        detail_url2 = reverse('accounts:payment-request-detail', args=[payment_request_id2])
        response = self.customer_client.get(detail_url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'DECLINED')
        
        # Refresh customer from database
        self.customer.refresh_from_db()
        
        # Verify balance is unchanged after decline
        response = self.customer_client.get(wallet_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['balance']), Decimal('400.00'))