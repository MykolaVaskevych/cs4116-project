import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { ServicesService } from '../../services/services-service/services.service';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-create-listing',
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './create-listing.component.html',
  styleUrl: './create-listing.component.css'
})
export class CreateListingComponent {
    isSubmitting = false;
    listingForm!: FormGroup;
    token: any;
    categories: any;
    errorMessage = ' '
    otherCategories: any
    serviceCat: any

    constructor(
        private services: ServicesService, private fb: FormBuilder, private router: Router, private route: ActivatedRoute
    ) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        console.log('token', this.token);

        this.listingForm = this.fb.group({
            description: ['', Validators.required],
            category: ['', Validators.required]
        });

        this.route.queryParams.subscribe((params: { [x: string]: string; }) => {
            this.serviceCat = JSON.parse(params['serviceCat']);
            console.log('cat',this.serviceCat);
        });

        console.log('ere')
        this.getServiceCategories();
    }

    getServiceCategories() {
        this.services.getServiceCategories(this.token).subscribe({
            next: (response) => {
                const mainCategories = ['Legal', 'Finance', 'Lifestyle'];

            // Filter categories into main and others
            this.categories = response.filter((cat: { name: string; }) => mainCategories.includes(cat.name));
            this.otherCategories = response.filter((cat: { name: string; }) => !mainCategories.includes(cat.name));

            console.log('Main categories:', this.categories);
            console.log('Other categories:', this.otherCategories);
            },
            error: (error) => {
                console.error('Error fetching categories', error);
            }
        });
    }
    onSubmit() {
        if (this.listingForm.valid) {
            this.errorMessage = '';
            this.isSubmitting = true;  // ✅ Show full-page spinner

            const selectedCategory = [...this.categories, ...this.otherCategories].find(
                (category: { id: any }) => category.id === Number(this.listingForm.value.category)
            );

            if (!selectedCategory) {
                this.errorMessage = 'Invalid category selected.';
                this.isSubmitting = false;
                return;
            }

            const servListing = {
                description: this.listingForm.value.description,
                category: selectedCategory.id,
                name: selectedCategory.name,
            };

            this.services.createService(this.token, servListing).subscribe({
                next: (response) => {
                    console.log('Service created successfully:', response);
                    this.isSubmitting = false;  // ✅ Hide spinner
                    this.router.navigate(['/service-listing'], {
                        queryParams: {
                            service: JSON.stringify(this.serviceCat)
                        }
                    });
                    // ✅ Redirect
                },
                error: (error) => {
                    console.error('Error creating service:', error);
                    this.isSubmitting = false;  // ✅ Hide spinner
                }
            });
        } else {
            this.errorMessage = 'Please fill all required fields.';
        }
    }


}
