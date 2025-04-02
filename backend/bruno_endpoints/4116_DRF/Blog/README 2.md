# Blog API Endpoints Documentation

This document outlines the endpoints available for the blog functionality in the system.

## Blog Categories

- **GET /api/blog/categories/** - List all blog categories
- **POST /api/blog/categories/** - Create a new blog category (moderator only)
- **GET /api/blog/categories/{id}/** - Get details of a specific category
- **PUT /api/blog/categories/{id}/** - Update a category (moderator only)
- **DELETE /api/blog/categories/{id}/** - Delete a category (moderator only)

## Blog Posts

- **GET /api/blog/posts/** - List all blog posts (with filtering and search)
  - Query params: `?author={id}&category={id}&is_published=true&search=keyword`
  - Ordering: `?ordering=views` or `?ordering=-created_at`
  
- **POST /api/blog/posts/** - Create a new blog post
  - Required fields: `title`, `content`
  - Optional fields: `summary`, `image`, `category`, `is_published`
  
- **GET /api/blog/posts/{id}/** - Get details of a specific blog post
  - Increments view count when viewed by non-author
  
- **GET /api/blog/posts/slug/{slug}/** - Get blog post by slug (SEO-friendly URL)
  - Increments view count when viewed by non-author
  
- **PUT /api/blog/posts/{id}/** - Update a blog post (author or moderator only)
  
- **DELETE /api/blog/posts/{id}/** - Delete a blog post (author or moderator only)

## User Blog Posts

- **GET /api/users/{id}/blog-posts/** - List all blog posts by a specific user
  - Shows only published posts unless viewer is moderator or the author

## Blog Comments

- **GET /api/blog/posts/{id}/comments/** - List all comments for a blog post
  
- **POST /api/blog/posts/{id}/comments/** - Create a new comment on a blog post
  - Required fields: `content`
  
- **GET /api/blog/comments/{id}/** - Get a specific comment
  
- **PUT /api/blog/comments/{id}/** - Update a comment (author or moderator only)
  
- **DELETE /api/blog/comments/{id}/** - Delete a comment (author or moderator only)

## Authentication

All endpoints require authentication with a valid JWT token.

## Permissions

- All users can create blog posts and comments
- Only authors and moderators can update/delete their own posts/comments
- Only moderators can manage blog categories
- Unpublished posts are only visible to their author and moderators