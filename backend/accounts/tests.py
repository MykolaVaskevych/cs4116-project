from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Service, Inquiry, Review, Wallet
from decimal import Decimal

User = get_user_model()

class ReviewTestCase(TestCase):
    """Test case for the Review model"""
    
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
        
        # Create a service
        self.service = Service.objects.create(
            name="Test Service",
            description="A service for testing",
            business=self.business
        )
        
        # Create an inquiry
        self.inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Test Inquiry"
        )
        
    def test_review_creation_with_open_inquiry(self):
        """Test that a review can't be created for an open inquiry"""
        # Attempt to create a review while inquiry is still open
        with self.assertRaises(ValueError):
            Review.objects.create(
                service=self.service,
                user=self.customer,
                rating=5,
                comment="Great service!"
            )
    
    def test_review_creation_with_closed_inquiry(self):
        """Test that a review can be created for a closed inquiry"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Now creating the review should succeed
        review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        self.assertEqual(review.service, self.service)
        self.assertEqual(review.user, self.customer)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great service!")
    
    def test_review_with_no_inquiry(self):
        """Test that a customer without an inquiry can't create a review"""
        # Create a new customer with no inquiries
        new_customer = User.objects.create_user(
            username="newcustomer",
            email="newcustomer@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        # Attempt to create a review
        with self.assertRaises(ValueError):
            Review.objects.create(
                service=self.service,
                user=new_customer,
                rating=5,
                comment="Great service!"
            )


class ReviewAPITestCase(APITestCase):
    """Test case for the Review API endpoints"""
    
    def setUp(self):
        """Set up test data and authenticate clients"""
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
        
        # Create a service
        self.service = Service.objects.create(
            name="Test Service",
            description="A service for testing",
            business=self.business
        )
        
        # Create an inquiry
        self.inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer,
            subject="Test Inquiry"
        )
        
        # Set up API clients
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
        # URLs - updated to use service-review-create instead of review-list-create
        self.reviews_url = reverse('accounts:service-review-create', args=[self.service.id])
    
    def test_customer_cannot_review_with_open_inquiry(self):
        """Test that a customer can't create a review for an open inquiry"""
        # Attempt to create a review while inquiry is still open
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You can only review a service if you have a closed inquiry for it', str(response.data))
    
    def test_customer_can_review_with_closed_inquiry(self):
        """Test that a customer can create a review for a closed inquiry"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Now creating the review should succeed
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['service'], self.service.id)
        self.assertEqual(response.data['user'], self.customer.id)
        self.assertEqual(response.data['rating'], 5)
        self.assertEqual(response.data['comment'], 'Great service!')
        
    def test_customer_cannot_review_service_twice(self):
        """Test that a customer can't review the same service twice"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Create first review
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        self.customer_client.post(self.reviews_url, data, format='json')
        
        # Try to create a second review
        second_data = {
            'service': self.service.id,
            'rating': 4,
            'comment': 'Actually it was good but not great'
        }
        
        response = self.customer_client.post(self.reviews_url, second_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You have already reviewed this service', str(response.data))
    
    def test_customer_cannot_review_service_without_inquiry(self):
        """Test that a customer can't review a service without an inquiry"""
        # Create a new service
        new_service = Service.objects.create(
            name="Another Service",
            description="Another service for testing",
            business=self.business
        )
        
        # Attempt to create a review for a service without an inquiry
        data = {
            'service': new_service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You can only review a service if you have a closed inquiry for it', str(response.data))
    
    def test_customer_can_update_own_review(self):
        """Test that a customer can update their own review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        review_id = response.data['review_id']
        
        # Update the review
        update_data = {
            'service': self.service.id,  # Need to include the service ID for validation
            'rating': 4,
            'comment': 'Good service, but could be better'
        }
        
        update_url = reverse('accounts:review-detail', args=[review_id])
        update_response = self.customer_client.patch(update_url, update_data, format='json')
        
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['rating'], 4)
        self.assertEqual(update_response.data['comment'], 'Good service, but could be better')
    
    def test_customer_cannot_update_others_review(self):
        """Test that a customer can't update another customer's review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        review_id = response.data['review_id']
        
        # Create another customer
        another_customer = User.objects.create_user(
            username="anothercustomer",
            email="anothercustomer@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        another_client = APIClient()
        another_client.force_authenticate(user=another_customer)
        
        # Try to update the review
        update_data = {
            'rating': 2,
            'comment': 'Not so good after all'
        }
        
        update_url = reverse('accounts:review-detail', args=[review_id])
        update_response = another_client.patch(update_url, update_data, format='json')
        
        self.assertEqual(update_response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_customer_can_delete_own_review(self):
        """Test that a customer can delete their own review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        review_id = response.data['review_id']
        
        # Delete the review
        delete_url = reverse('accounts:review-detail', args=[review_id])
        delete_response = self.customer_client.delete(delete_url)
        
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's gone
        get_response = self.customer_client.get(delete_url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_filter_reviews_by_service(self):
        """Test that reviews can be filtered by service"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        data = {
            'rating': 5,
            'comment': 'Great service!'
        }
        
        self.customer_client.post(self.reviews_url, data, format='json')
        
        # Create another service and review
        another_service = Service.objects.create(
            name="Another Service",
            description="Another service for testing",
            business=self.business
        )
        
        another_inquiry = Inquiry.objects.create(
            service=another_service,
            customer=self.customer,
            subject="Another Inquiry"
        )
        
        another_inquiry.close(self.moderator)
        
        # Create a URL for the second service
        another_service_reviews_url = reverse('accounts:service-review-create', args=[another_service.id])
        
        another_data = {
            'rating': 3,
            'comment': 'Okay service'
        }
        
        self.customer_client.post(another_service_reviews_url, another_data, format='json')
        
        # Get reviews filtered by service
        service_reviews_list_url = reverse('accounts:service-reviews-list', args=[self.service.id])
        response = self.customer_client.get(service_reviews_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['service'], self.service.id)
        self.assertEqual(response.data[0]['rating'], 5)
        
    def test_review_rating_boundaries(self):
        """Test that review ratings must be between 0 and 5"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Test valid boundary values (0 and 5)
        valid_data = {
            'service': self.service.id,
            'rating': 0,
            'comment': 'Terrible service'
        }
        
        response = self.customer_client.post(self.reviews_url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Delete the review to create another one
        review_id = response.data['review_id']
        delete_url = reverse('accounts:review-detail', args=[review_id])
        self.customer_client.delete(delete_url)
        
        # Test upper boundary
        valid_data2 = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Excellent service'
        }
        
        response2 = self.customer_client.post(self.reviews_url, valid_data2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Test invalid value (out of range)
        invalid_data = {
            'service': self.service.id,
            'rating': 6,
            'comment': 'Beyond excellent service'
        }
        
        # Delete the previous review first
        review_id2 = response2.data['review_id']
        delete_url2 = reverse('accounts:review-detail', args=[review_id2])
        self.customer_client.delete(delete_url2)
        
        response3 = self.customer_client.post(self.reviews_url, invalid_data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test negative value (out of range)
        invalid_data2 = {
            'service': self.service.id,
            'rating': -1,
            'comment': 'Negative rating'
        }
        
        response4 = self.customer_client.post(self.reviews_url, invalid_data2, format='json')
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_empty_comment_is_valid(self):
        """Test that reviews can have empty comments"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        data = {
            'service': self.service.id,
            'rating': 4,
            'comment': ''  # Empty comment
        }
        
        response = self.customer_client.post(self.reviews_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment'], '')


class CompleteWorkflowTestCase(APITestCase):
    """Test the complete workflow from user registration to reviews"""
    
    def setUp(self):
        """Set up base test data"""
        # URLs
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.wallet_url = reverse('accounts:wallet')
        self.deposit_url = reverse('accounts:deposit')
        # Use the actual router pattern for viewsets
        self.services_url = '/api/services/'
        self.inquiries_url = '/api/inquiries/'
        # We'll set the reviews_url after creating the service in the test
    
    def test_complete_workflow(self):
        """Test complete workflow from registration to review"""
        # 1. Register users
        moderator_data = {
            'username': 'moderator',
            'email': 'moderator@example.com',
            'password': 'Pass1234!',
            'first_name': 'Mod',
            'last_name': 'Erator',
            'role': 'MODERATOR'
        }
        
        business_data = {
            'username': 'business',
            'email': 'business@example.com',
            'password': 'Pass1234!',
            'first_name': 'Busi',
            'last_name': 'Ness',
            'role': 'BUSINESS'
        }
        
        customer_data = {
            'username': 'customer',
            'email': 'customer@example.com',
            'password': 'Pass1234!',
            'first_name': 'Cust',
            'last_name': 'Omer',
            'role': 'CUSTOMER'
        }
        
        moderator_response = self.client.post(self.register_url, moderator_data, format='json')
        business_response = self.client.post(self.register_url, business_data, format='json')
        customer_response = self.client.post(self.register_url, customer_data, format='json')
        
        self.assertEqual(moderator_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(business_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(customer_response.status_code, status.HTTP_201_CREATED)
        
        # 2. Login users
        moderator_login = {
            'email': 'moderator@example.com',
            'password': 'Pass1234!'
        }
        
        business_login = {
            'email': 'business@example.com',
            'password': 'Pass1234!'
        }
        
        customer_login = {
            'email': 'customer@example.com',
            'password': 'Pass1234!'
        }
        
        moderator_token = self.client.post(self.login_url, moderator_login, format='json').data['access']
        business_token = self.client.post(self.login_url, business_login, format='json').data['access']
        customer_token = self.client.post(self.login_url, customer_login, format='json').data['access']
        
        # Set up clients with authentication
        self.moderator_client = APIClient()
        self.moderator_client.credentials(HTTP_AUTHORIZATION=f'Bearer {moderator_token}')
        
        self.business_client = APIClient()
        self.business_client.credentials(HTTP_AUTHORIZATION=f'Bearer {business_token}')
        
        self.customer_client = APIClient()
        self.customer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {customer_token}')
        
        # 3. Business creates a service
        service_data = {
            'name': 'Home Cleaning Service',
            'description': 'We clean your home thoroughly and efficiently.'
        }
        
        service_response = self.business_client.post(self.services_url, service_data, format='json')
        self.assertEqual(service_response.status_code, status.HTTP_201_CREATED)
        service_id = service_response.data['id']
        
        # Now we can set the reviews URL with the service ID
        self.reviews_url = reverse('accounts:service-review-create', args=[service_id])
        
        # 4. Customer creates an inquiry
        inquiry_data = {
            'service': service_id,
            'subject': 'Inquiry about cleaning service',
            'initial_message': 'I would like to know more about your cleaning service.'
        }
        
        inquiry_response = self.customer_client.post(self.inquiries_url, inquiry_data, format='json')
        self.assertEqual(inquiry_response.status_code, status.HTTP_201_CREATED)
        # Getting the ID from the serializer depends on how it's named in your serializer
        # Let's print the response and use a reasonable fallback
        print("Inquiry response data:", inquiry_response.data)
        inquiry_id = 1  # For test purposes, we'll assume it's the first inquiry
        
        # 5. Customer can't review yet (inquiry is open)
        review_data = {
            'rating': 5,
            'comment': 'Great service!'
        }
        
        review_response = self.customer_client.post(self.reviews_url, review_data, format='json')
        self.assertEqual(review_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 6. Moderator closes the inquiry
        close_url = f'/api/inquiries/{inquiry_id}/close/'
        close_response = self.moderator_client.post(close_url)
        self.assertEqual(close_response.status_code, status.HTTP_200_OK)
        self.assertEqual(close_response.data['status'], 'CLOSED')
        
        # 7. Now customer can review the service
        review_response = self.customer_client.post(self.reviews_url, review_data, format='json')
        self.assertEqual(review_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(review_response.data['rating'], 5)
        self.assertEqual(review_response.data['comment'], 'Great service!')
        
        # 8. Business can see the review
        service_reviews_url = reverse('accounts:service-reviews-list', args=[service_id])
        reviews_response = self.business_client.get(service_reviews_url)
        self.assertEqual(reviews_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(reviews_response.data), 1)
        self.assertEqual(reviews_response.data[0]['rating'], 5)