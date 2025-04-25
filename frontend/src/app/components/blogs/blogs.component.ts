import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { BlogService, BlogCategory, BlogPost, PaginatedResponse } from '../../services/blog.service';
import { CommonModule } from '@angular/common';
import { UserProfileService } from '../../services/user-profile.service';
import { Validators } from 'ngx-editor';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, takeUntil } from 'rxjs/operators';

// For use in the template
declare global {
  interface Window {
    Math: typeof Math;
  }
}

@Component({
    selector: 'app-blogs',
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink],
    templateUrl: './blogs.component.html',
    styleUrl: './blogs.component.css'
})
export class BlogsComponent implements OnInit, OnDestroy {
    // Math object for template use
    Math = Math;
    // Loading and authentication states
    isLoading = false;
    token: string | null = null;
    
    // Data collections
    categories: BlogCategory[] = [];
    blogs: BlogPost[] = [];
    filteredBlogs: BlogPost[] = [];
    user: any;
    
    // Search and filtering
    searchTerm = '';
    selectedCategory: number | null = null;
    sortOption = 'newest';
    private searchSubject = new Subject<string>();
    private destroy$ = new Subject<void>();
    

    constructor(
        private blogService: BlogService, 
        private userProfileService: UserProfileService,
        private router: Router
    ) {
        // Initialize filteredBlogs to prevent undefined error
        this.filteredBlogs = [];
    }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        if (!this.token) {
            this.router.navigate(['/login']);
            return;
        }
        
        // Set up search debounce to prevent too many API calls while typing
        this.searchSubject.pipe(
            debounceTime(400), // Wait for 400ms pause in events
            distinctUntilChanged(),
            takeUntil(this.destroy$)
        ).subscribe(term => {
            this.searchTerm = term;
            // No pagination
            this.loadBlogs();
        });
        
        // Load initial data
        this.loadCategories();
        this.loadBlogs();
    }

    ngOnDestroy() {
        this.destroy$.next();
        this.destroy$.complete();
    }

    // Load all categories (uses caching in the service)
    loadCategories() {
        if (!this.token) return;
        
        // Initialize categories to an empty array
        this.categories = [];
        
        this.blogService.getBlogCategories(this.token).subscribe({
            next: (categories) => {
                if (Array.isArray(categories)) {
                    this.categories = categories;
                } else {
                    console.error('Categories response has unexpected format');
                    this.categories = [];
                }
            },
            error: (error) => {
                console.error('Error loading categories:', error);
                this.categories = [];
            }
        });
    }

    // Load all blog posts
    loadBlogs() {
        if (!this.token) return;
        
        this.isLoading = true;
        
        // Determine sort parameter for API
        let sortParam: string | undefined;
        switch (this.sortOption) {
            case 'newest':
                sortParam = '-created_at'; // Descending by date
                break;
            case 'oldest':
                sortParam = 'created_at'; // Ascending by date
                break;
            case 'a-z':
                sortParam = 'title'; // Alphabetical
                break;
            case 'z-a':
                sortParam = '-title'; // Reverse alphabetical
                break;
        }
        
        // Get all blog posts - backend pagination disabled
        this.blogService.getBlogPosts(
            this.token,
            undefined, // No pagination needed anymore
            undefined, // No pagination needed anymore
            this.selectedCategory || undefined,
            this.searchTerm || undefined,
            sortParam
        ).subscribe({
            next: (response: any) => {
                // Handle both array and paginated responses for compatibility
                if (Array.isArray(response)) {
                    // Backend is returning an array directly
                    this.blogs = response;
                    this.filteredBlogs = this.blogs;
                } else if (response && response.results) {
                    // Backend is returning a paginated response (fallback)
                    this.blogs = response.results;
                    this.filteredBlogs = this.blogs;
                } else {
                    // Unexpected response format
                    console.error('Unexpected blog response format');
                    this.blogs = [];
                    this.filteredBlogs = [];
                }
                
                this.isLoading = false;
            },
            error: (error) => {
                console.error('Error loading blogs:', error);
                this.blogs = []; 
                this.filteredBlogs = [];
                this.isLoading = false;
            }
        });
    }

    // Note: This method is available for future use when user-specific blog features are added

    // Search and filter methods
    onSearch(event: Event) {
        const input = event.target as HTMLInputElement;
        this.searchSubject.next(input.value);
    }

    clearSearch() {
        this.searchTerm = '';
        this.loadBlogs();
    }

    filterByCategory(categoryId: number | null) {
        this.selectedCategory = categoryId;
        this.loadBlogs();
    }

    sortBlogs() {
        this.loadBlogs();
    }

    // Navigation to blog detail
    viewBlogDetail(blog: BlogPost) {
        this.router.navigate(['/blogs', blog.slug]);
    }
    
    }