import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { BlogService } from '../../services/blog.service';
import { UserProfileService } from '../../services/user-profile.service';

@Component({
  selector: 'app-blog-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, RouterLink],
  templateUrl: './blog-detail.component.html',
  styleUrl: './blog-detail.component.css'
})
export class BlogDetailComponent implements OnInit {
  isLoading = true;
  token: string | null = null;
  blog: any;
  comments: any[] = [];
  showComments = false;
  profilePic = 'icon.png';
  user: any;
  commentForm: FormGroup;
  blogSlug: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private blogService: BlogService,
    private userProfileService: UserProfileService,
    private fb: FormBuilder
  ) {
    this.commentForm = this.fb.group({
      content: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.token = localStorage.getItem('access');
    if (!this.token) {
      this.router.navigate(['/login']);
      return;
    }

    // Get the slug from the route
    this.route.paramMap.subscribe(params => {
      this.blogSlug = params.get('slug');
      if (this.blogSlug) {
        this.loadBlog();
      } else {
        this.router.navigate(['/blogs']);
      }
    });

    // Load user profile for commenting
    this.loadUserProfile();
  }

  loadBlog(): void {
    if (!this.blogSlug || !this.token) return;

    this.isLoading = true;
    this.blogService.getPostBySlug(this.token, this.blogSlug).subscribe({
      next: (response) => {
        this.blog = response;
        this.loadComments(this.blog.id);
      },
      error: (error) => {
        console.error('Error loading blog:', error);
        this.isLoading = false;
        this.router.navigate(['/blogs']);
      }
    });
  }

  loadComments(blogId: number): void {
    if (!this.token) return;

    // Initialize comments as empty array
    this.comments = [];
    
    this.blogService.getPostComments(this.token, blogId).subscribe({
      next: (response) => {
        // Check if response is an array and use it
        if (Array.isArray(response)) {
          this.comments = response;
          console.log('Comments loaded:', this.comments.length);
        } else {
          console.error('Expected comments to be an array but got:', response);
          this.comments = [];
        }
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading comments:', error);
        this.comments = [];
        this.isLoading = false;
      }
    });
  }

  loadUserProfile(): void {
    if (!this.token) return;

    this.userProfileService.getProfile(this.token).subscribe({
      next: (response) => {
        this.user = response;
        if (this.user.profile_image) {
          this.profilePic = this.user.profile_image;
        }
      },
      error: (error) => {
        console.error('Error loading user profile:', error);
      }
    });
  }

  toggleComments(): void {
    this.showComments = !this.showComments;
  }

  submitComment(): void {
    if (this.commentForm.invalid || !this.token || !this.blog) {
      console.error('Cannot submit comment: form invalid or missing token/blog');
      return;
    }

    console.log('Submitting comment:', this.commentForm.value);
    this.isLoading = true;
    
    this.blogService.createComment(this.token, this.blog.id, this.commentForm.value).subscribe({
      next: (response) => {
        console.log('Comment posted successfully:', response);
        this.commentForm.reset();
        
        // Add the new comment to the comments array immediately
        if (response) {
          // If we receive a proper response object
          const newComment = {
            ...response,
            author_name: this.user.username || 'You',
            author_image: this.user.profile_image || this.profilePic
          };
          this.comments.push(newComment);
        }
        
        // Also reload all comments from server to be sure
        this.loadComments(this.blog.id);
      },
      error: (error) => {
        console.error('Error submitting comment:', error);
        this.isLoading = false;
      }
    });
  }
}