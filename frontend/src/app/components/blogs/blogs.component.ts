import { Component } from '@angular/core';
import { FormGroup, FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BlogService } from '../../services/blog.service';
import { CommonModule } from '@angular/common';
import { UserProfileService } from '../../services/user-profile.service';
import { Validators } from 'ngx-editor';
import { MarkdownModule } from 'ngx-markdown';

@Component({
    selector: 'app-blogs',
    imports: [CommonModule, FormsModule, ReactiveFormsModule, MarkdownModule],
    templateUrl: './blogs.component.html',
    styleUrl: './blogs.component.css'
})
export class BlogsComponent {
    isLoading = false;
    token: any;
    categories: any;
    blogs: any
    user: any
    selectedBlog: any
    comments: any[] = [];
    showCommentsSlug: string | null = null;
    profilepic = '';
    commentForm: FormGroup;

    constructor(
        private blogService: BlogService, private fb: FormBuilder, private userProfileService: UserProfileService
    ) {
        this.commentForm = this.fb.group({
            content: ['', Validators.required] // form control for the comment input
        });
    }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        console.log('token', this.token);

        this.getBlogPosts()
        this.getBlogCategories();
        this.loadUserProfile()
    }

    getBlogCategories() {
        this.blogService.getBlogCategories(this.token).subscribe({
            next: (response) => {
                this.categories = response;
                console.log('categories', this.categories);

            },
            error: (error) => {
                console.error('Error fetching categories', error);
            }
        });
    }

    getBlogPosts() {
        this.blogService.getBlogPosts(this.token).subscribe({
            next: (response) => {
                this.blogs = response;
                console.log('blogs', this.blogs);

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    getBlogPostsByCat(id: any) {
        this.blogService.getPostsByCategory(this.token, id).subscribe({
            next: (response) => {
                this.blogs = response;
                this.comments = []
                console.log('blogs', this.blogs);
                this.getPostComments(id);

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    getBlogPostsBySlug(blog: any) {
        this.blogService.getPostBySlug(this.token, blog.slug).subscribe({
            next: (response) => {
                this.selectedBlog = response;
                this.comments = []
                console.log('blog by slug', this.selectedBlog);
                this.getPostComments(blog.id)

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    loadUserProfile() {


        this.userProfileService.getProfile(this.token).subscribe({
            next: (response) => {
                this.user = response;
                console.log('user', this.user)

                if (this.user.profile_image)
                    this.profilepic = this.user.profile_image
                else
                    this.profilepic = 'icon.png'
            },
            error: (error) => {
                console.error('Error fetching profile', error);
            }
        });

    }

    getPostComments(id: number) {
        this.isLoading = true
        this.blogService.getPostComments(this.token, id).subscribe({
            next: (response) => {
                this.isLoading = false
                console.log(id, response)
                this.comments = response
                console.log('comments', this.comments);
            },
            error: (error) => {
                this.isLoading = false
                console.error('Error fetching comments', error);
            }
        });
    }

    toggleComments(slug: string, event: MouseEvent) {
        event.stopPropagation(); // prevents triggering blog card click
        this.showCommentsSlug = this.showCommentsSlug === slug ? null : slug;
    }

    createComment(id: any) {
        if (this.commentForm.invalid) {
            this.commentForm.markAllAsTouched();
        }

        console.log('comm form val', this.commentForm.value)
        this.isLoading = true

        this.blogService.createComment(this.token, id, this.commentForm.value).subscribe({
            next: (response) => {
                this.isLoading = false
                console.log('comment ceated successfully', response);
                this.commentForm.reset()
                this.getPostComments(id)
            },
            error: (error) => {
                this.isLoading = false
                console.error('Error creating comments', error);
            }
        });

    }


}