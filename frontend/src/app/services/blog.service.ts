import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { catchError, map, shareReplay, tap } from 'rxjs/operators';
import { environment } from '../../env/environment';

export interface BlogPost {
  id: number;
  title: string;
  slug: string;
  content: string;
  summary: string;
  image: string;
  author: number;
  author_name: string;
  author_image: string;
  author_bio: string;
  category: number;
  category_name: string;
  created_at: string;
  updated_at: string;
  views: number;
  is_published: boolean;
}

export interface BlogCategory {
  id: number;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
  post_count: number;
}

export interface BlogComment {
  id: number;
  blog_post: number;
  author: number;
  author_name: string;
  author_role: string;
  author_image: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class BlogService {
  private apiUrl = `${environment.apiHost}/api/blog`;
  
  // Cache for categories (doesn't change often)
  private categoriesCache$: Observable<BlogCategory[]> | null = null;
  
  // Individual blog post cache
  private blogPostCache: Map<string, { data: BlogPost, timestamp: number }> = new Map();
  
  // Cache expiration time (10 minutes)
  private CACHE_EXPIRATION = 10 * 60 * 1000;

  constructor(private http: HttpClient) { }

  /**
   * Get all blog categories with caching
   */
  getBlogCategories(token: string): Observable<BlogCategory[]> {
    if (!this.categoriesCache$) {
      const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
      
      this.categoriesCache$ = this.http.get<BlogCategory[]>(`${this.apiUrl}/categories`, { headers }).pipe(
        // Cache the result
        shareReplay(1),
        // Handle errors
        catchError(error => {
          console.error('Error fetching blog categories:', error);
          return of([]);
        })
      );
    }
    
    return this.categoriesCache$;
  }

  /**
   * Get blog posts with pagination, filtering, and sorting
   */
  getBlogPosts(
    token: string, 
    page: number = 1, 
    pageSize: number = 10,
    category?: number,
    search?: string,
    sort?: string
  ): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    // Add optional filters
    if (category) {
      params = params.set('category', category.toString());
    }
    
    if (search) {
      params = params.set('search', search);
    }
    
    if (sort) {
      params = params.set('ordering', sort);
    }
    
    return this.http.get<any>(`${this.apiUrl}/posts`, { 
      headers,
      params
    }).pipe(
      catchError(error => {
        console.error('Error fetching blog posts:', error);
        
        // Return an empty result that works with both formats
        return of([]);
      })
    );
  }

  /**
   * Get posts by category
   */
  getPostsByCategory(
    token: string, 
    categoryId: number
  ): Observable<any> {
    return this.getBlogPosts(token, undefined, undefined, categoryId);
  }

  /**
   * Get a single blog post by slug with caching
   */
  getPostBySlug(token: string, slug: string): Observable<BlogPost> {
    const cacheKey = slug;
    const cachedBlog = this.blogPostCache.get(cacheKey);
    const now = Date.now();
    
    // Return cached version if still valid
    if (cachedBlog && (now - cachedBlog.timestamp < this.CACHE_EXPIRATION)) {
      return of(cachedBlog.data);
    }
    
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    
    return this.http.get<BlogPost>(`${this.apiUrl}/posts/slug/${slug}`, { headers }).pipe(
      tap(blog => {
        // Cache the result
        this.blogPostCache.set(cacheKey, {
          data: blog,
          timestamp: now
        });
      }),
      catchError(error => {
        console.error(`Error fetching blog post with slug ${slug}:`, error);
        throw error;
      })
    );
  }

  /**
   * Get comments for a blog post
   */
  getPostComments(token: string, id: number): Observable<BlogComment[]> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    
    return this.http.get<BlogComment[]>(`${this.apiUrl}/posts/${id}/comments`, { headers }).pipe(
      catchError(error => {
        console.error(`Error fetching comments for blog ${id}:`, error);
        return of([]);
      })
    );
  }

  /**
   * Create a new blog post
   */
  createBlogPost(token: string, blogData: any): Observable<BlogPost> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    return this.http.post<BlogPost>(`${this.apiUrl}/posts/`, blogData, { headers }).pipe(
      tap(() => {
        // Invalidate the cache when a new post is created
        this.invalidateListCache();
      }),
      catchError(error => {
        console.error('Error creating blog post:', error);
        throw error;
      })
    );
  }
  
  /**
   * Create a new blog post with image
   * Uses FormData to handle file uploads
   */
  createBlogPostWithImage(token: string, formData: FormData): Observable<BlogPost> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`);
    // Don't set Content-Type here, it will be set automatically with the boundary for FormData
    
    return this.http.post<BlogPost>(`${this.apiUrl}/posts/`, formData, { headers }).pipe(
      tap(() => {
        // Invalidate the cache when a new post is created
        this.invalidateListCache();
      }),
      catchError(error => {
        console.error('Error creating blog post with image:', error);
        throw error;
      })
    );
  }

  /**
   * Create a comment on a blog post
   */
  createComment(token: string, id: number, data: any): Observable<BlogComment> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    return this.http.post<BlogComment>(`${this.apiUrl}/posts/${id}/comments/`, data, { headers }).pipe(
      catchError(error => {
        console.error(`Error creating comment for blog ${id}:`, error);
        throw error;
      })
    );
  }
  
  /**
   * Clear all caches
   */
  clearCaches(): void {
    this.categoriesCache$ = null;
    this.blogPostCache.clear();
  }
  
  /**
   * Invalidate just the list cache (for when new posts are added)
   */
  private invalidateListCache(): void {
    // The categories cache needs to be invalidated as post counts may have changed
    this.categoriesCache$ = null;
  }
}
