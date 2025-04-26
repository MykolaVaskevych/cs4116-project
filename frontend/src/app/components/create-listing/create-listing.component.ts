import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ServicesService } from '../../services/services-service/services.service';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-create-listing',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './create-listing.component.html',
  styleUrl: './create-listing.component.css'
})
export class CreateListingComponent implements OnInit {
    isSubmitting = false;
    listingForm!: FormGroup;
    token: any;
    categories: any = [];
    errorMessage: string = '';
    otherCategories: any = [];
    serviceCat: any;
    
    // Image handling
    selectedImage: File | null = null;
    imagePreviewSrc: string = '';

    constructor(
        private services: ServicesService, 
        private fb: FormBuilder, 
        private router: Router, 
        private route: ActivatedRoute
    ) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        
        this.listingForm = this.fb.group({
            description: ['', Validators.required],
            category: ['', Validators.required],
            fixed_price: [0, [Validators.required, Validators.min(0)]]
        });

        this.route.queryParams.subscribe((params: { [x: string]: string; }) => {
            if (params['serviceCat']) {
                this.serviceCat = JSON.parse(params['serviceCat']);
            }
        });

        this.getServiceCategories();
    }

    getServiceCategories() {
        this.services.getServiceCategories(this.token).subscribe({
            next: (response) => {
                const mainCategories = ['Legal', 'Finance', 'Lifestyle'];

                // Filter categories into main and others
                this.categories = response.filter((cat: { name: string; }) => 
                    mainCategories.includes(cat.name));
                this.otherCategories = response.filter((cat: { name: string; }) => 
                    !mainCategories.includes(cat.name));
            },
            error: (error) => {
                console.error('Error fetching categories', error);
                this.errorMessage = 'Failed to load categories. Please try again.';
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
        
        // Generate preview
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
    
    cancelListing() {
        this.router.navigate(['/service-listing'], {
            queryParams: {
                service: JSON.stringify(this.serviceCat)
            }
        });
    }

    onSubmit() {
        if (this.listingForm.invalid) {
            // Mark all fields as touched to show validation errors
            Object.keys(this.listingForm.controls).forEach(field => {
                const control = this.listingForm.get(field);
                control?.markAsTouched();
            });
            
            this.errorMessage = 'Please fill all required fields correctly.';
            return;
        }

        this.errorMessage = '';
        this.isSubmitting = true;

        const selectedCategory = [...this.categories, ...this.otherCategories].find(
            (category: { id: any }) => category.id === Number(this.listingForm.value.category)
        );

        if (!selectedCategory) {
            this.errorMessage = 'Invalid category selected.';
            this.isSubmitting = false;
            return;
        }

        // Use FormData to handle image upload
        const formData = new FormData();
        formData.append('description', this.listingForm.value.description);
        formData.append('category', selectedCategory.id);
        formData.append('name', selectedCategory.name);
        formData.append('fixed_price', this.listingForm.value.fixed_price);
        
        // Add the image if selected
        if (this.selectedImage) {
            formData.append('logo', this.selectedImage, this.selectedImage.name);
        }

        this.services.createServiceWithImage(this.token, formData).subscribe({
            next: (response) => {
                console.log('Service created successfully:', response);
                this.isSubmitting = false;
                this.router.navigate(['/service-listing'], {
                    queryParams: {
                        service: JSON.stringify(this.serviceCat)
                    }
                });
            },
            error: (error) => {
                console.error('Error creating service:', error);
                this.isSubmitting = false;
                this.errorMessage = 'Failed to create service. Please try again.';
            }
        });
    }
}
