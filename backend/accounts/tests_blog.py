from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils.text import slugify
from .models import (
    User, BlogCategory, BlogPost, BlogComment
)

User = get_user_model()

class BlogModelTestCase(TestCase):
    """Test case for the Blog models"""
    
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
        
        # Create blog category
        self.category = BlogCategory.objects.create(
            name="Education",
            description="Educational content about our services"
        )
    
    def test_blog_category_creation(self):
        """Test blog category creation"""
        self.assertEqual(self.category.name, "Education")
        self.assertEqual(self.category.description, "Educational content about our services")
    
    def test_blog_post_creation(self):
        """Test blog post creation"""
        blog_post = BlogPost.objects.create(
            title="How to Use Our Platform",
            content="This is a detailed guide on how to use our platform...",
            summary="A beginner's guide to our platform",
            author=self.customer,
            category=self.category,
            slug="how-to-use-our-platform",
            is_published=True
        )
        
        self.assertEqual(blog_post.title, "How to Use Our Platform")
        self.assertEqual(blog_post.author, self.customer)
        self.assertEqual(blog_post.category, self.category)
        self.assertEqual(blog_post.slug, "how-to-use-our-platform")
        self.assertEqual(blog_post.is_published, True)
        self.assertEqual(blog_post.views, 0)
    
    def test_blog_post_slug_uniqueness(self):
        """Test that blog post slugs must be unique"""
        # Create first post
        BlogPost.objects.create(
            title="How to Use Our Platform",
            content="This is a detailed guide on how to use our platform...",
            author=self.customer,
            slug="how-to-use-our-platform",
            is_published=True
        )
        
        # Create another post with the same title/slug
        # This should raise an error
        with self.assertRaises(Exception):
            BlogPost.objects.create(
                title="How to Use Our Platform",
                content="Another guide with the same title",
                author=self.business,
                slug="how-to-use-our-platform",
                is_published=True
            )
    
    def test_blog_post_view_increment(self):
        """Test that blog post view count can be incremented"""
        blog_post = BlogPost.objects.create(
            title="View Count Test",
            content="Testing view count increment",
            author=self.customer,
            slug="view-count-test",
            is_published=True
        )
        
        self.assertEqual(blog_post.views, 0)
        
        # Increment views
        blog_post.increment_views()
        self.assertEqual(blog_post.views, 1)
        
        # Increment again
        blog_post.increment_views()
        self.assertEqual(blog_post.views, 2)
    
    def test_blog_comment_creation(self):
        """Test blog comment creation"""
        blog_post = BlogPost.objects.create(
            title="Comment Test",
            content="Testing comments",
            author=self.customer,
            slug="comment-test",
            is_published=True
        )
        
        comment = BlogComment.objects.create(
            blog_post=blog_post,
            author=self.business,
            content="Great article!"
        )
        
        self.assertEqual(comment.blog_post, blog_post)
        self.assertEqual(comment.author, self.business)
        self.assertEqual(comment.content, "Great article!")


class BlogAPITestCase(APITestCase):
    """Test case for the Blog API endpoints"""
    
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
        
        # Set up API clients
        self.customer_client = APIClient()
        self.customer_client.force_authenticate(user=self.customer)
        
        self.business_client = APIClient()
        self.business_client.force_authenticate(user=self.business)
        
        self.moderator_client = APIClient()
        self.moderator_client.force_authenticate(user=self.moderator)
        
        # Create blog category
        self.category = BlogCategory.objects.create(
            name="Education",
            description="Educational content about our services"
        )
        
        # URLs
        self.categories_url = reverse('accounts:blog-category-list')
        self.blog_posts_url = reverse('accounts:blog-post-list')
        self.user_posts_url = reverse('accounts:user-blog-posts', args=[self.customer.id])
    
    def test_list_blog_categories(self):
        """Test listing blog categories"""
        response = self.customer_client.get(self.categories_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Education")
    
    def test_create_blog_category_as_customer(self):
        """Test that regular customers cannot create blog categories"""
        data = {
            'name': 'Tutorials',
            'description': 'Step-by-step tutorials'
        }
        
        response = self.customer_client.post(self.categories_url, data, format='json')
        
        # Should be forbidden for non-moderators
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_blog_category_as_moderator(self):
        """Test that moderators can create blog categories"""
        data = {
            'name': 'Tutorials',
            'description': 'Step-by-step tutorials'
        }
        
        response = self.moderator_client.post(self.categories_url, data, format='json')
        
        # Should be allowed for moderators
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Tutorials')
    
    def test_create_blog_post(self):
        """Test creating a blog post"""
        data = {
            'title': 'Getting Started Guide',
            'content': 'Here is how to get started with our platform...',
            'summary': 'A quick start guide',
            'category': self.category.id,
            'is_published': True
        }
        
        response = self.customer_client.post(self.blog_posts_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Getting Started Guide')
        # Slug should be auto-generated
        self.assertEqual(response.data['slug'], 'getting-started-guide')
        self.assertEqual(response.data['author'], self.customer.id)
    
    def test_list_blog_posts(self):
        """Test listing blog posts"""
        # Create a few blog posts
        BlogPost.objects.create(
            title="Post 1",
            content="Content 1",
            author=self.customer,
            slug="post-1",
            is_published=True
        )
        
        BlogPost.objects.create(
            title="Post 2",
            content="Content 2",
            author=self.business,
            slug="post-2",
            is_published=True
        )
        
        BlogPost.objects.create(
            title="Draft Post",
            content="Draft content",
            author=self.customer,
            slug="draft-post",
            is_published=False
        )
        
        # Customer should see all published posts plus their own drafts
        response = self.customer_client.get(self.blog_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # 2 published + 1 own draft
        
        # Business should see all published posts plus their own drafts (none here)
        response = self.business_client.get(self.blog_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 published, no drafts
        
        # Moderator should see all posts (published and drafts)
        response = self.moderator_client.get(self.blog_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)  # All posts
    
    def test_get_blog_post_by_slug(self):
        """Test getting a blog post by slug"""
        # Create a blog post
        blog_post = BlogPost.objects.create(
            title="Slug Test",
            content="Testing slug retrieval",
            author=self.customer,
            slug="slug-test",
            is_published=True
        )
        
        url = reverse('accounts:blog-post-by-slug', args=[blog_post.slug])
        response = self.business_client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Slug Test')
        self.assertEqual(response.data['slug'], 'slug-test')
        
        # Check that views were incremented (viewed by someone other than author)
        blog_post.refresh_from_db()
        self.assertEqual(blog_post.views, 1)
    
    def test_update_blog_post(self):
        """Test updating a blog post"""
        # Create a blog post
        blog_post = BlogPost.objects.create(
            title="Update Test",
            content="Original content",
            author=self.customer,
            slug="update-test",
            is_published=True
        )
        
        # For ViewSet-based routes, we use the detail action URL pattern
        url = f'/api/blog/posts/{blog_post.id}/'
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'is_published': False
        }
        
        # Author should be able to update their own post
        response = self.customer_client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')
        self.assertEqual(response.data['content'], 'Updated content')
        self.assertEqual(response.data['is_published'], False)
        
        # Create another post for testing permissions
        another_post = BlogPost.objects.create(
            title="Another Test",
            content="Another content",
            author=self.customer,
            slug="another-test",
            is_published=True
        )
        
        another_url = f'/api/blog/posts/{another_post.id}/'
        
        # Another user should not be able to update the post
        response = self.business_client.patch(another_url, {'title': 'Hacked Title'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Moderator should be able to update any post
        response = self.moderator_client.patch(url, {'title': 'Moderator Update'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Moderator Update')
    
    def test_delete_blog_post(self):
        """Test deleting a blog post"""
        # Create a blog post
        blog_post = BlogPost.objects.create(
            title="Delete Test",
            content="Content to delete",
            author=self.customer,
            slug="delete-test",
            is_published=True
        )
        
        # Create another blog post owned by customer
        another_post = BlogPost.objects.create(
            title="Another Delete Test",
            content="More content to delete",
            author=self.customer,
            slug="another-delete-test",
            is_published=True
        )
        
        url = f'/api/blog/posts/{blog_post.id}/'
        another_url = f'/api/blog/posts/{another_post.id}/'
        
        # Another user should not be able to delete the post
        response = self.business_client.delete(another_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Verify post still exists
        self.assertTrue(BlogPost.objects.filter(id=another_post.id).exists())
        
        # Author should be able to delete their own post
        response = self.customer_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify post is deleted
        self.assertFalse(BlogPost.objects.filter(id=blog_post.id).exists())
    
    def test_filter_blog_posts_by_category(self):
        """Test filtering blog posts by category"""
        # Create another category
        category2 = BlogCategory.objects.create(
            name="Tutorials",
            description="Step-by-step tutorials"
        )
        
        # Create posts in different categories
        BlogPost.objects.create(
            title="Education Post",
            content="Educational content",
            author=self.customer,
            category=self.category,
            slug="education-post",
            is_published=True
        )
        
        BlogPost.objects.create(
            title="Tutorial Post",
            content="Tutorial content",
            author=self.customer,
            category=category2,
            slug="tutorial-post",
            is_published=True
        )
        
        # Filter by education category
        response = self.customer_client.get(f"{self.blog_posts_url}?category={self.category.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Education Post')
        
        # Filter by tutorial category
        response = self.customer_client.get(f"{self.blog_posts_url}?category={category2.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Tutorial Post')
    
    def test_search_blog_posts(self):
        """Test searching blog posts"""
        # Create posts with different content
        BlogPost.objects.create(
            title="Python Tutorial",
            content="Learn Python programming",
            author=self.customer,
            slug="python-tutorial",
            is_published=True
        )
        
        BlogPost.objects.create(
            title="JavaScript Guide",
            content="Learn JavaScript programming",
            author=self.customer,
            slug="javascript-guide",
            is_published=True
        )
        
        # Search for Python
        response = self.customer_client.get(f"{self.blog_posts_url}?search=Python")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Tutorial')
        
        # Search for programming (should return both)
        response = self.customer_client.get(f"{self.blog_posts_url}?search=programming")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_blog_comments(self):
        """Test blog comment functionality"""
        # Create a blog post
        blog_post = BlogPost.objects.create(
            title="Comment Test",
            content="Test content",
            author=self.customer,
            slug="comment-test",
            is_published=True
        )
        
        # Create a comment
        comments_url = reverse('accounts:blog-comments-list', args=[blog_post.id])
        comment_data = {
            'content': 'This is a great post!'
        }
        
        response = self.business_client.post(comments_url, comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'This is a great post!')
        self.assertEqual(response.data['author'], self.business.id)
        
        # List comments
        response = self.customer_client.get(comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Update comment
        comment_id = response.data[0]['id']
        comment_url = reverse('accounts:blog-comment-detail', args=[comment_id])
        update_data = {
            'content': 'Updated comment'
        }
        
        # Author should be able to update their comment
        response = self.business_client.patch(comment_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Updated comment')
        
        # Another user should not be able to update the comment
        response = self.customer_client.patch(comment_url, {'content': 'Hacked comment'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Moderator should be able to update any comment
        response = self.moderator_client.patch(comment_url, {'content': 'Moderator edit'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete comment
        response = self.business_client.delete(comment_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify comment is deleted
        self.assertFalse(BlogComment.objects.filter(id=comment_id).exists())
    
    def test_commenting_on_unpublished_posts(self):
        """Test that users cannot comment on unpublished posts unless they are author/moderator"""
        # Create an unpublished blog post
        blog_post = BlogPost.objects.create(
            title="Unpublished Post",
            content="Draft content",
            author=self.customer,
            slug="unpublished-post",
            is_published=False
        )
        
        comments_url = reverse('accounts:blog-comments-list', args=[blog_post.id])
        comment_data = {
            'content': 'This comment should fail'
        }
        
        # Regular user cannot comment on unpublished post
        response = self.business_client.post(comments_url, comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Author should be able to comment on their unpublished post
        response = self.customer_client.post(comments_url, comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Moderator should be able to comment on unpublished post
        comment_data = {
            'content': 'Moderator comment on unpublished post'
        }
        response = self.moderator_client.post(comments_url, comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_user_blog_posts_endpoint(self):
        """Test the endpoint for getting a user's blog posts"""
        # Create posts by different users
        BlogPost.objects.create(
            title="Customer Post 1",
            content="Content by customer",
            author=self.customer,
            slug="customer-post-1",
            is_published=True
        )
        
        BlogPost.objects.create(
            title="Customer Post 2",
            content="More content by customer",
            author=self.customer,
            slug="customer-post-2",
            is_published=False  # Draft
        )
        
        BlogPost.objects.create(
            title="Business Post",
            content="Content by business",
            author=self.business,
            slug="business-post",
            is_published=True
        )
        
        # Get customer's posts - as customer (should see published and unpublished)
        response = self.customer_client.get(self.user_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both posts
        
        # Get customer's posts - as business (should see only published)
        response = self.business_client.get(self.user_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only published
        
        # Get customer's posts - as moderator (should see all)
        response = self.moderator_client.get(self.user_posts_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both posts