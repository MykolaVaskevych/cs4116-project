from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Service, Inquiry, Review, ReviewComment

User = get_user_model()


class ReviewModelTestCase(TestCase):
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
    
    def test_review_requires_closed_inquiry(self):
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
    
    def test_duplicate_review_prevention(self):
        """Test that a customer can't create multiple reviews for the same service"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Create first review
        Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        # Attempt to create a second review
        with self.assertRaises(ValueError):
            Review.objects.create(
                service=self.service,
                user=self.customer,
                rating=4,
                comment="Second review"
            )


class ReviewCommentModelTestCase(TestCase):
    """Test case for the ReviewComment model"""
    
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
        
        # Create another customer
        self.customer2 = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="password123",
            role=User.Role.CUSTOMER
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
        
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        self.review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=4,
            comment="Good service but could be better"
        )
    
    def test_business_owner_can_comment(self):
        """Test that the business owner can comment on a review of their service"""
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.business,
            content="Thank you for your feedback!"
        )
        
        self.assertEqual(comment.review, self.review)
        self.assertEqual(comment.author, self.business)
        self.assertEqual(comment.content, "Thank you for your feedback!")
    
    def test_moderator_can_comment(self):
        """Test that a moderator can comment on any review"""
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.moderator,
            content="Moderator note: This feedback has been verified."
        )
        
        self.assertEqual(comment.review, self.review)
        self.assertEqual(comment.author, self.moderator)
    
    def test_customer_cannot_comment(self):
        """Test that regular customers cannot comment on reviews"""
        # Even the review author should not be able to comment
        with self.assertRaises(ValueError):
            ReviewComment.objects.create(
                review=self.review,
                author=self.customer,
                content="Adding more context to my review."
            )
        
        # Other customers definitely cannot comment
        with self.assertRaises(ValueError):
            ReviewComment.objects.create(
                review=self.review,
                author=self.customer2,
                content="I disagree with this review."
            )


class ReviewAPITestCase(APITestCase):
    """Test case for the Review API endpoints"""
    
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
        
        # Create another customer for testing permissions
        self.another_customer = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        # Set up API clients
        # Unauthenticated client for testing auth requirements
        self.unauthenticated_client = APIClient()
        
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.another_customer_client = APIClient()
        self.another_customer_client.force_authenticate(user=self.another_customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
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
        
        # Create another service by the same business
        self.service2 = Service.objects.create(
            name="Another Service",
            description="Another service for testing",
            business=self.business
        )
        
        # Create an inquiry for the second service
        self.inquiry2 = Inquiry.objects.create(
            service=self.service2,
            customer=self.customer,
            subject="Another Inquiry"
        )
        
        # Create an inquiry for the first service by another customer
        self.another_inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.another_customer,
            subject="Second Customer Inquiry"
        )
    
    def test_list_service_reviews(self):
        """Test listing reviews for a specific service"""
        # Close inquiries and create reviews
        self.inquiry.close(self.moderator)
        self.another_inquiry.close(self.moderator)
        
        # Create reviews
        review1 = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        review2 = Review.objects.create(
            service=self.service,
            user=self.another_customer,
            rating=3,
            comment="Average service."
        )
        
        # Test listing reviews for service 1
        url = reverse('accounts:service-reviews-list', args=[self.service.id])
        response = self.customer_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Ensure reviews are ordered by newest first
        self.assertEqual(response.data[0]['review_id'], review2.review_id)
        self.assertEqual(response.data[1]['review_id'], review1.review_id)
    
    def test_create_service_review(self):
        """Test creating a review for a service"""
        # Close the inquiry
        self.inquiry.close(self.moderator)
        
        # Create a review
        url = reverse('accounts:service-review-create', args=[self.service.id])
        data = {
            'rating': 4,
            'comment': 'Good service!'
        }
        
        response = self.customer_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['comment'], 'Good service!')
        self.assertEqual(response.data['user'], self.customer.id)
        self.assertEqual(response.data['service'], self.service.id)
    
    def test_create_review_without_closed_inquiry(self):
        """Test that a review cannot be created without a closed inquiry"""
        # Inquiry is not closed
        url = reverse('accounts:service-review-create', args=[self.service.id])
        data = {
            'rating': 4,
            'comment': 'Good service!'
        }
        
        response = self.customer_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You can only review a service if you have a closed inquiry for it', str(response.data))
    
    def test_list_user_reviews(self):
        """Test listing reviews by a specific user"""
        # Close inquiries and create reviews
        self.inquiry.close(self.moderator)
        self.inquiry2.close(self.moderator)
        
        # Create reviews for two different services
        Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        Review.objects.create(
            service=self.service2,
            user=self.customer,
            rating=4,
            comment="Good service!"
        )
        
        # Test listing reviews by the customer
        url = reverse('accounts:user-reviews-list', args=[self.customer.id])
        response = self.customer_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_update_own_review(self):
        """Test that a user can update their own review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        # Update the review
        url = reverse('accounts:review-detail', args=[review.review_id])
        data = {
            'rating': 4,
            'comment': 'Good service, but could be better'
        }
        
        response = self.customer_client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 4)
        self.assertEqual(response.data['comment'], 'Good service, but could be better')
    
    def test_cannot_update_others_review(self):
        """Test that a user cannot update another user's review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        # Try to update the review as another customer
        url = reverse('accounts:review-detail', args=[review.review_id])
        data = {
            'rating': 2,
            'comment': 'Not so good after all'
        }
        
        response = self.another_customer_client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_review(self):
        """Test that a user can delete their own review"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        # Delete the review
        url = reverse('accounts:review-detail', args=[review.review_id])
        response = self.customer_client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's gone
        get_response = self.customer_client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_authentication_required(self):
        """Test that all review endpoints require authentication"""
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        
        review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=5,
            comment="Great service!"
        )
        
        # Test listing service reviews
        url = reverse('accounts:service-reviews-list', args=[self.service.id])
        response = self.unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test creating a review
        url = reverse('accounts:service-review-create', args=[self.service.id])
        data = {
            'rating': 4,
            'comment': 'Good service!'
        }
        response = self.unauthenticated_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test getting review details
        url = reverse('accounts:review-detail', args=[review.review_id])
        response = self.unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test updating a review
        data = {
            'rating': 3,
            'comment': 'Updated comment'
        }
        response = self.unauthenticated_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReviewCommentAPITestCase(APITestCase):
    """Test case for the Review Comment API endpoints"""
    
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
        
        # Create another customer for testing permissions
        self.another_customer = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        # Create another business user
        self.another_business = User.objects.create_user(
            username="business2",
            email="business2@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        # Set up API clients
        # Unauthenticated client for testing auth requirements
        self.unauthenticated_client = APIClient()
        
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
        self.another_business_client = APIClient()
        self.another_business_client.force_authenticate(user=self.another_business)
        
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
        
        # Close the inquiry and create a review
        self.inquiry.close(self.moderator)
        self.review = Review.objects.create(
            service=self.service,
            user=self.customer,
            rating=3,
            comment="Average service, could be better."
        )
    
    def test_business_owner_can_comment_on_review(self):
        """Test that a business owner can comment on a review of their service"""
        url = reverse('accounts:review-comments-list', args=[self.review.review_id])
        data = {
            'content': 'Thank you for your feedback! We will improve.'
        }
        
        response = self.business_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['author'], self.business.id)
    
    def test_moderator_can_comment_on_review(self):
        """Test that a moderator can comment on any review"""
        url = reverse('accounts:review-comments-list', args=[self.review.review_id])
        data = {
            'content': 'Moderator note: This review has been verified.'
        }
        
        response = self.moderator_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], data['content'])
        self.assertEqual(response.data['author'], self.moderator.id)
    
    def test_customer_cannot_comment_on_review(self):
        """Test that customers cannot comment on reviews"""
        url = reverse('accounts:review-comments-list', args=[self.review.review_id])
        data = {
            'content': 'I want to add more context to my review.'
        }
        
        response = self.customer_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_other_business_cannot_comment(self):
        """Test that business owners cannot comment on reviews for services they don't own"""
        url = reverse('accounts:review-comments-list', args=[self.review.review_id])
        data = {
            'content': 'I can offer a better service!'
        }
        
        response = self.another_business_client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_own_comment(self):
        """Test that comment authors can update their own comments"""
        # Create a comment
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.business,
            content="Thanks for your feedback."
        )
        
        # Update the comment
        url = reverse('accounts:review-comment-detail', args=[self.review.review_id, comment.comment_id])
        data = {
            'content': 'Thank you for your feedback! We have made improvements.'
        }
        
        response = self.business_client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], data['content'])
    
    def test_cannot_update_others_comment(self):
        """Test that users cannot update comments they didn't author"""
        # Create a comment by the business
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.business,
            content="Thanks for your feedback."
        )
        
        # Try to update as moderator
        url = reverse('accounts:review-comment-detail', args=[self.review.review_id, comment.comment_id])
        data = {
            'content': 'Edited by moderator'
        }
        
        response = self.moderator_client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_own_comment(self):
        """Test that comment authors can delete their own comments"""
        # Create a comment
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.business,
            content="Thanks for your feedback."
        )
        
        # Delete the comment
        url = reverse('accounts:review-comment-detail', args=[self.review.review_id, comment.comment_id])
        response = self.business_client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify it's gone
        get_response = self.business_client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_comment_authentication_required(self):
        """Test that all review comment endpoints require authentication"""
        # Test listing comments
        url = reverse('accounts:review-comments-list', args=[self.review.review_id])
        response = self.unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test creating a comment
        data = {
            'content': 'This should not work without authentication'
        }
        response = self.unauthenticated_client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Create a comment to test other endpoints
        comment = ReviewComment.objects.create(
            review=self.review,
            author=self.business,
            content="Thanks for your feedback."
        )
        
        # Test retrieving a comment
        url = reverse('accounts:review-comment-detail', args=[self.review.review_id, comment.comment_id])
        response = self.unauthenticated_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test updating a comment
        data = {
            'content': 'Updated content'
        }
        response = self.unauthenticated_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test deleting a comment
        response = self.unauthenticated_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)