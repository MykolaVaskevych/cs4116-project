from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from io import BytesIO
from PIL import Image
from .models import Service, Category
import os
import tempfile

User = get_user_model()

def create_test_image(width=512, height=512, color='blue', format='JPEG'):
    """Helper function to create a test image"""
    file = BytesIO()
    image = Image.new('RGB', (width, height), color=color)
    image.save(file, format=format)
    file.name = f'test_{color}.jpg'
    file.seek(0)
    return file

class UserProfileImageTests(APITestCase):
    """Test case for user profile image functionality"""
    
    def setUp(self):
        # Create users with different roles
        self.customer = User.objects.create_user(
            username="customer",
            email="customer@example.com",
            password="password123",
            role=User.Role.CUSTOMER
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.customer)
        
        # Create test image
        self.test_image = create_test_image()
        self.image_data = SimpleUploadedFile(
            name='test_image.jpg',
            content=self.test_image.getvalue(),
            content_type='image/jpeg'
        )
        
    def test_update_profile_image(self):
        """Test that users can update their profile image"""
        url = reverse('accounts:profile')
        
        # Test file upload with multipart form
        response = self.client.patch(
            url, 
            {'profile_image': self.image_data},
            format='multipart'
        )
        
        self.customer.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.customer.profile_image)
        self.assertTrue(os.path.exists(self.customer.profile_image.path))
        
        # Check that the image was resized to the standard size
        with Image.open(self.customer.profile_image.path) as img:
            self.assertEqual(img.size, (512, 512))
            
    def test_delete_profile_image(self):
        """Test that users can delete their profile image"""
        # First, upload an image
        url = reverse('accounts:profile')
        self.client.patch(
            url, 
            {'profile_image': self.image_data},
            format='multipart'
        )
        
        # Then request to delete it
        response = self.client.patch(
            url, 
            {'profile_image': None},
            format='json'
        )
        
        self.customer.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.customer.profile_image)


class ServiceImageTests(APITestCase):
    """Test case for service image functionality"""
    
    def setUp(self):
        # Create a business user
        self.business = User.objects.create_user(
            username="business",
            email="business@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.business)
        
        # Create a service
        self.service = Service.objects.create(
            name="Test Service",
            description="A service for testing",
            business=self.business
        )
        
        # Create a category
        self.category = Category.objects.create(
            name="Test Category",
            description="A category for testing"
        )
        
        # Create test image
        self.test_image = create_test_image()
        self.image_data = SimpleUploadedFile(
            name='test_logo.jpg',
            content=self.test_image.getvalue(),
            content_type='image/jpeg'
        )
        
    def test_add_service_logo(self):
        """Test that business users can add a logo to their service"""
        # Get service detail using the router URL with reverse()
        url = reverse('accounts:service-detail', kwargs={'pk': self.service.id})
        
        # Test file upload with multipart form
        response = self.client.patch(
            url, 
            {'logo': self.image_data},
            format='multipart'
        )
        
        self.service.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.service.logo)
        self.assertTrue(os.path.exists(self.service.logo.path))
        
        # Check that the image was resized to the standard size
        with Image.open(self.service.logo.path) as img:
            self.assertEqual(img.size, (512, 512))
            
    def test_update_service_with_category(self):
        """Test that business users can update a service with a category"""
        url = reverse('accounts:service-detail', kwargs={'pk': self.service.id})
        
        response = self.client.patch(
            url, 
            {'category': self.category.id},
            format='json'
        )
        
        self.service.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.service.category.id, self.category.id)

    def test_other_users_cannot_update_service_logo(self):
        """Test that non-owners cannot update a service logo"""
        # Create another user
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        
        url = reverse('accounts:service-detail', kwargs={'pk': self.service.id})
        
        response = other_client.patch(
            url, 
            {'logo': self.image_data},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def tearDown(self):
        # Clean up test image files
        if self.service.logo:
            if os.path.exists(self.service.logo.path):
                os.remove(self.service.logo.path)


class CategoryTests(APITestCase):
    """Test case for category functionality"""
    
    def setUp(self):
        # Create a moderator user who can manage categories
        self.moderator = User.objects.create_user(
            username="moderator",
            email="moderator@example.com",
            password="password123",
            role=User.Role.MODERATOR
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.moderator)
        
    def test_create_category(self):
        """Test that moderators can create categories"""
        url = reverse('accounts:category-list')
        
        data = {
            'name': 'New Category',
            'description': 'A new category for testing'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(Category.objects.first().name, 'New Category')
        
    def test_list_categories(self):
        """Test listing available categories"""
        # Create several categories
        Category.objects.create(name="Category 1", description="First category")
        Category.objects.create(name="Category 2", description="Second category")
        Category.objects.create(name="Category 3", description="Third category")
        
        url = reverse('accounts:category-list')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        
    def test_filter_services_by_category(self):
        """Test that services can be filtered by category"""
        # Create a business user
        business = User.objects.create_user(
            username="business",
            email="business@example.com",
            password="password123",
            role=User.Role.BUSINESS
        )
        
        # Create categories
        category1 = Category.objects.create(name="Category 1", description="First category")
        category2 = Category.objects.create(name="Category 2", description="Second category")
        
        # Create services
        service1 = Service.objects.create(
            name="Service 1", 
            description="First service", 
            business=business,
            category=category1
        )
        
        service2 = Service.objects.create(
            name="Service 2", 
            description="Second service", 
            business=business,
            category=category1
        )
        
        service3 = Service.objects.create(
            name="Service 3", 
            description="Third service", 
            business=business,
            category=category2
        )
        
        # Test filtering
        url = reverse('accounts:service-list')
        response = self.client.get(f"{url}?category={category1.id}")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        response = self.client.get(f"{url}?category={category2.id}")
        self.assertEqual(len(response.data), 1)