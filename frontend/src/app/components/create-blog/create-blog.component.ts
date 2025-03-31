import { Component } from '@angular/core';
import { BlogService } from '../../services/blog.service';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { QuillModule } from 'ngx-quill';
import { Router } from '@angular/router';

@Component({
    selector: 'app-create-blog',
    standalone: true,
    imports: [CommonModule, FormsModule, ReactiveFormsModule, QuillModule],
    templateUrl: './create-blog.component.html',
    styleUrl: './create-blog.component.css'
})
export class CreateBlogComponent {
    blogForm!: FormGroup;
    token: any;
    categories: any;
    errorMessage = ' '
    isSubmitting = false

    constructor(
        private blogService: BlogService, private fb: FormBuilder, private router: Router
    ) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        console.log('token', this.token);

        this.blogForm = this.fb.group({
            title: ['', Validators.required],
            category: ['', Validators.required],
            content: ['', Validators.required]
        });

        this.getBlogCategories();
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

    onSubmit() {
        if (this.blogForm.valid) {
            this.errorMessage = '';
            this.isSubmitting = true;  // ✅ Show full-page spinner


            const selectedCategory = this.categories.find(
                (category: { id: any; }) => category.id === Number(this.blogForm.value.category)
            );

            const blogPost = {
                title: this.blogForm.value.title,
                content: this.blogForm.value.content,
                category: selectedCategory.id,
                category_name: selectedCategory.name,
            }

            console.log('blogPost', blogPost)

            this.blogService.createBlogPost(this.token, blogPost)
                .subscribe(
                    response => {
                        console.log('Blog created successfully:', response);
                    this.isSubmitting = false;  // ✅ Hide spinner

                    this.router.navigate(['/blogs']);

                    },
                    error => {
                        console.error('Error creating blog:', error);
                    }
                );


        } else {
            this.errorMessage = 'Please fill all required fields.';

            // Find and log invalid fields
            Object.keys(this.blogForm.controls).forEach(field => {
                const control = this.blogForm.get(field);
                if (control?.invalid) {
                    console.log(`Invalid field: ${field}`, control.errors);
                }
            });
        }
    }

}
