from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

User = get_user_model()

class PasswordChangeTestCase(APITestCase):
    def setUp(self):
        # Create test users
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
        
        # Set up API clients
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
        # URL for password change endpoint
        self.change_password_url = reverse('accounts:change_password')

    def test_change_password_successful(self):
        """Test successful password change"""
        valid_data = {
            'old_password': 'password123',
            'new_password': 'NewSecure456!',
            'confirm_password': 'NewSecure456!'
        }
        
        response = self.customer_client.post(self.change_password_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password updated successfully')
        
        # Verify password actually changed
        self.customer.refresh_from_db()
        self.assertTrue(check_password('NewSecure456!', self.customer.password))
        
        # Test authentication with new password
        login_url = reverse('accounts:login')
        login_data = {
            'email': 'customer@example.com',
            'password': 'NewSecure456!'
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_old_password(self):
        """Test with incorrect old password"""
        invalid_old_password = {
            'old_password': 'wrongpassword', 
            'new_password': 'NewSecurePass789!',
            'confirm_password': 'NewSecurePass789!'
        }
        
        response = self.customer_client.post(self.change_password_url, invalid_old_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)

    def test_change_password_mismatched_passwords(self):
        """Test with mismatched new passwords"""
        mismatched_passwords = {
            'old_password': 'password123', 
            'new_password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        
        response = self.customer_client.post(self.change_password_url, mismatched_passwords, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('confirm_password', response.data)

    def test_change_password_weak_password(self):
        """Test with weak new password that doesn't meet requirements"""
        weak_password = {
            'old_password': 'password123', 
            'new_password': 'password',
            'confirm_password': 'password'
        }
        
        response = self.customer_client.post(self.change_password_url, weak_password, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', response.data)

    def test_change_password_unauthenticated(self):
        """Test with unauthenticated user"""
        valid_data = {
            'old_password': 'password123',
            'new_password': 'NewSecure456!',
            'confirm_password': 'NewSecure456!'
        }
        
        self.client.logout()
        response = self.client.post(self.change_password_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_different_roles(self):
        """Test password change with different user roles"""
        valid_data = {
            'old_password': 'password123',
            'new_password': 'NewSecure456!',
            'confirm_password': 'NewSecure456!'
        }
        
        # Test with business user
        response = self.business_client.post(self.change_password_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.business.refresh_from_db()
        self.assertTrue(check_password('NewSecure456!', self.business.password))
        
        # Test with moderator user
        response = self.moderator_client.post(self.change_password_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.moderator.refresh_from_db()
        self.assertTrue(check_password('NewSecure456!', self.moderator.password))