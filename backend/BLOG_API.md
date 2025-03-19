# Blog/Education API Implementation

This document outlines the blog and educational content functionality that has been added to the platform.

## Models

### 1. BlogCategory
- Represents categories for organizing blog posts
- Fields: name, description, created_at, updated_at
- Only moderators can create or modify categories

### 2. BlogPost
- Core model for blog/educational content
- Fields:
  - title: Title of the blog post
  - slug: URL-friendly version of the title (auto-generated)
  - content: Main content of the blog post
  - summary: Optional short description
  - author: User who created the post
  - category: Optional category classification
  - image: Optional featured image
  - created_at/updated_at: Timestamps
  - is_published: Publication status
  - views: Counter for tracking popularity
- SEO-friendly URLs via the slug field
- View tracking functionality

### 3. BlogComment
- Comments left by users on blog posts
- Fields: blog_post, author, content, created_at, updated_at
- Any user can comment on published posts
- Authors can only modify their own comments (or moderators)

## API Endpoints

### Blog Categories
- `GET /api/blog/categories/` - List all categories
- `POST /api/blog/categories/` - Create a category (moderator only)
- `GET /api/blog/categories/{id}/` - Category details
- `PUT/PATCH /api/blog/categories/{id}/` - Update a category (moderator only)
- `DELETE /api/blog/categories/{id}/` - Delete a category (moderator only)

### Blog Posts
- `GET /api/blog/posts/` - List all posts (with filtering and search)
- `POST /api/blog/posts/` - Create a new post
- `GET /api/blog/posts/{id}/` - Post details
- `GET /api/blog/posts/slug/{slug}/` - Get post by slug (SEO-friendly URL)
- `PUT/PATCH /api/blog/posts/{id}/` - Update a post (author or moderator only)
- `DELETE /api/blog/posts/{id}/` - Delete a post (author or moderator only)

### User Blog Posts
- `GET /api/users/{id}/blog-posts/` - List all posts by a specific user

### Blog Comments
- `GET /api/blog/posts/{id}/comments/` - List all comments for a post
- `POST /api/blog/posts/{id}/comments/` - Create a comment on a post
- `GET /api/blog/comments/{id}/` - Get a specific comment
- `PUT/PATCH /api/blog/comments/{id}/` - Update a comment (author or moderator only)
- `DELETE /api/blog/comments/{id}/` - Delete a comment (author or moderator only)

## Features

1. **User-Generated Content**: Any authenticated user can create educational blog posts
2. **Categorization**: Posts can be organized into categories
3. **Search & Filtering**: Posts can be searched and filtered by various criteria
4. **SEO-Friendly URLs**: Posts have slugs for better URL structure
5. **View Tracking**: System tracks post popularity via view counts
6. **Comments**: Users can engage by commenting on posts
7. **Permission System**:
   - All users can read published posts
   - Authors can only edit/delete their own content
   - Moderators have oversight capabilities
   - Unpublished posts are only visible to authors and moderators

## Testing

Bruno API endpoint files have been created for testing the API:
- List categories
- Create category (moderator only)
- List blog posts (with filtering options)
- Create blog post
- Get blog post by slug
- Create blog comment
- List user's blog posts

## Integration

The blog functionality is fully integrated with the existing:
- User authentication system
- Permission framework
- Image handling (resizing)
- Database infrastructure