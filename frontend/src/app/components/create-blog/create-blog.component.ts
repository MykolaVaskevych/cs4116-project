import { Component, OnInit } from '@angular/core';
import { BlogService } from '../../services/blog.service';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { QuillModule } from 'ngx-quill';
import { Router } from '@angular/router';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';

@Component({
    selector: 'app-create-blog',
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule, QuillModule],
    templateUrl: './create-blog.component.html',
    styleUrl: './create-blog.component.css'
})
export class CreateBlogComponent implements OnInit {
    blogForm!: FormGroup;
    token: string | null = null;
    categories: any[] = [];
    errorMessage = '';
    isSubmitting = false;
    selectedImage: File | null = null;
    imagePreviewSrc: string = '';

    constructor(
        private blogService: BlogService, 
        private fb: FormBuilder, 
        private router: Router,
        private sanitizer: DomSanitizer
    ) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        if (!this.token) {
            this.router.navigate(['/login']);
            return;
        }

        this.initForm();
        this.getBlogCategories();
    }

    initForm() {
        this.blogForm = this.fb.group({
            title: ['', [Validators.required, Validators.maxLength(200)]],
            summary: ['', [Validators.required, Validators.maxLength(500)]],
            category: ['', Validators.required],
            content: ['', Validators.required]
        });
    }

    getBlogCategories() {
        if (!this.token) return;
        
        this.blogService.getBlogCategories(this.token).subscribe({
            next: (response) => {
                if (Array.isArray(response)) {
                    this.categories = response;
                } else {
                    console.error('Categories response has unexpected format');
                    this.categories = [];
                }
            },
            error: (error) => {
                console.error('Error fetching categories:', error);
                this.errorMessage = 'Failed to load blog categories. Please try again.';
            }
        });
    }

    onImageSelected(event: Event) {
        const fileInput = event.target as HTMLInputElement;
        
        if (!fileInput.files || fileInput.files.length === 0) {
            return;
        }
        
        const file = fileInput.files[0];
        this.selectedImage = file;
        
        const reader = new FileReader();
        reader.onload = () => {
            this.imagePreviewSrc = reader.result as string;
        };
        
        reader.readAsDataURL(file);
    }
    
    removeImage() {
        this.selectedImage = null;
        this.imagePreviewSrc = '';
    }

    cancelPost() {
        this.router.navigate(['/blogs']);
    }

    onSubmit() {
        if (this.blogForm.invalid) {
            this.errorMessage = 'Please fill all required fields correctly.';
            
            // Mark all fields as touched to show validation errors
            Object.keys(this.blogForm.controls).forEach(field => {
                const control = this.blogForm.get(field);
                control?.markAsTouched();
            });
            
            return;
        }

        this.errorMessage = '';
        this.isSubmitting = true;

        // Generate a slug from the title
        const slug = this.generateSlug(this.blogForm.value.title);
        
        try {
            // Use FormData for multipart/form-data to support the image upload
            const formData = new FormData();
            
            // Add all form fields
            formData.append('title', this.blogForm.value.title);
            formData.append('slug', slug);
            formData.append('summary', this.blogForm.value.summary);
            formData.append('content', this.blogForm.value.content);
            formData.append('category', this.blogForm.value.category);
            formData.append('is_published', 'true');
            
            // Add the image if selected
            if (this.selectedImage) {
                formData.append('image', this.selectedImage, this.selectedImage.name);
            }
            
            // Use the FormData method to handle the image upload
            this.blogService.createBlogPostWithImage(this.token!, formData).subscribe({
                next: (response) => {
                    this.isSubmitting = false;
                    this.router.navigate(['/blogs']);
                },
                error: (error) => {
                    console.error('Error creating blog post:', error);
                    this.isSubmitting = false;
                    this.errorMessage = error.error?.detail || 'Failed to create blog post. Please try again.';
                }
            });
        } catch (error) {
            console.error('Error preparing blog data:', error);
            this.isSubmitting = false;
            this.errorMessage = 'An unexpected error occurred. Please try again.';
        }
    }

    // Generate a URL-friendly slug from the title
    private generateSlug(title: string): string {
        return title
            .toLowerCase()
            .replace(/[^\w\s-]/g, '') // Remove special characters
            .replace(/\s+/g, '-')     // Replace spaces with hyphens
            .replace(/--+/g, '-')     // Replace multiple hyphens with single hyphen
            .trim();
    }
}
