from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import User

class UrlsTestCase(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
            is_superuser=True
        )
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="regular",
            email="regular@example.com",
            password="regularpass",
            role=User.Role.CUSTOMER
        )
        
        # Set up clients
        self.client = Client()
        self.admin_client = Client()
        self.admin_client.force_login(self.admin_user)
        
        self.regular_client = Client()
        self.regular_client.force_login(self.regular_user)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "OK")
    
    def test_admin_urls(self):
        """Test admin site URLs"""
        # Test admin login page
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        
        # Test admin index for authenticated admin user
        response = self.admin_client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Test admin index for regular user (should deny access)
        response = self.regular_client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_direct_login(self):
        """Test direct login endpoint"""
        # Test GET request
        response = self.client.get('/direct-login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Direct Admin Login', response.content.decode())
        
        # Test successful POST request
        response = self.client.post('/direct-login/', {
            'email': 'admin@example.com',
            'password': 'adminpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to admin
        self.assertEqual(response.url, '/admin/')
        
        # Test failed POST request
        response = self.client.post('/direct-login/', {
            'email': 'admin@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('authenticated', response.json())
        self.assertFalse(response.json()['authenticated'])
        
        # Test non-existent user
        response = self.client.post('/direct-login/', {
            'email': 'nonexistent@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['authenticated'])
        self.assertFalse(response.json()['user_info']['exists'])
    
    def test_admin_debug(self):
        """Test admin debug endpoint"""
        # Test GET request
        response = self.client.get('/admin-debug/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Django Admin Debug', response.content.decode())
        
        # Test POST request to create admin
        response = self.client.post('/admin-debug/', {
            'action': 'create_admin'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Admin user created', response.content.decode())
        
        # Test POST request to login (which would redirect)
        response = self.client.post('/admin-debug/', {
            'action': 'login'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/admin/')
    
    def test_create_admin(self):
        """Test create admin endpoint"""
        # Delete existing admin to ensure clean test
        User.objects.filter(email='admin@example.com').delete()
        
        # Test creating admin
        response = self.client.post('/create-admin/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify admin was created
        self.assertTrue(User.objects.filter(email='admin@example.com').exists())
        admin = User.objects.get(email='admin@example.com')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        
        # Test recreating admin (should delete and recreate)
        response = self.client.post('/create-admin/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(response.json()['deleted_existing'])
    
    def test_dashboard_view(self):
        """Test dashboard view"""
        # Test dashboard view
        dashboard_url = reverse('admin:accounts_dashboard')
        response = self.admin_client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)
        
        # Test access denied for regular user
        response = self.regular_client.get(dashboard_url)
        self.assertEqual(response.status_code, 302)  # Redirect to login