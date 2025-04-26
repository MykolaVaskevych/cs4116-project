import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ServicesService } from '../../services/services-service/services.service';
import { FormsModule } from '@angular/forms';
import { filter } from 'rxjs';


@Component({
    selector: 'app-service-listing',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './service-listing.component.html',
    styleUrl: './service-listing.component.css'
})
export class ServiceListingComponent {
    empty=false
    searchTerm: string = '';
    serviceCat : any
    isProvider : any
    fetchedServices: any
    filteredServices: any
    token: any
    other=false
    
    // Filter variables
    selectedCategory: number | null = null;
    priceMin: number | null = null;
    priceMax: number | null = null;
    categories: any[] = [];

    constructor(private router: Router, private route: ActivatedRoute, private services: ServicesService
    ) { }

    ngOnInit() {
        console.log('searchterm', this.searchTerm)
        this.token =  localStorage.getItem('access');
        console.log('token', this.token)

        this.route.queryParams.subscribe(params => {
            this.serviceCat = JSON.parse(params['service']);
            console.log('serviceCat received:', this.serviceCat);
            
            let filter = null;
            if (params['filter']) {
                filter = JSON.parse(params['filter']);
                console.log('Filter received:', filter);
            }

            if(this.serviceCat.length>1){
                this.other = true
                this.getAllServices()
                this.getServiceCategories()
                
                if (filter && filter.isFromHome && filter.category) {
                    setTimeout(() => {
                        this.selectedCategory = this.categories.find(
                            (cat: any) => cat.name === filter.category
                        )?.id || null;
                        this.filterServices();
                    }, 500);
                }
            }
            else {
                this.getServicesByCategories()
            }
        });

        this.isProvider = JSON.parse(localStorage.getItem('isProvider') || 'false');
        console.log(this.isProvider, 'isprovider');
    }
    
    // Get service categories for filtering
    getServiceCategories() {
        this.services.getServiceCategories(this.token).subscribe({
            next: (response) => {
                this.categories = response;
                console.log('Categories loaded:', this.categories);
            },
            error: (error) => {
                console.error('Error fetching categories', error);
            }
        });
    }

    redirectToCreateListing(){
        this.router.navigate(['/create-listing'], {
            queryParams: {
                serviceCat: JSON.stringify(this.serviceCat)
            }
        });
    }

    filterServices() {
        this.filteredServices = this.fetchedServices.filter((service: any) => {
            // Text search filter
            const matchesSearch = this.searchTerm 
                ? service.description.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                  service.business_name?.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
                  service.category_name?.toLowerCase().includes(this.searchTerm.toLowerCase())
                : true;
            
            // Category filter
            const matchesCategory = this.selectedCategory 
                ? service.category === this.selectedCategory 
                : true;
            
            // Price range filters
            const matchesMinPrice = this.priceMin !== null 
                ? service.fixed_price >= this.priceMin 
                : true;
                
            const matchesMaxPrice = this.priceMax !== null 
                ? service.fixed_price <= this.priceMax 
                : true;
            
            return matchesSearch && matchesCategory && matchesMinPrice && matchesMaxPrice;
        });

        console.log('filtered services:', this.filteredServices);
    }
    
    filterByCategory(categoryId: number | null) {
        this.selectedCategory = categoryId;
        this.filterServices();
    }
    
    clearFilters() {
        this.priceMin = null;
        this.priceMax = null;
        this.selectedCategory = null;
        this.filterServices();
    }

      getServicesByCategories() {
        this.services.getServicesByCategories(this.token, this.serviceCat.id).subscribe({
          next: (response) => {
            this.fetchedServices = response;
            this.filteredServices = [...this.fetchedServices];
            console.log('services', this.fetchedServices);
          },
          error: (error) => {
            if (error.status === 404) {
                this.empty=true
                console.warn('No services found for this category.');
            } else {
                console.error('Error fetching services', error);
            }
          }
        });

      }

      getAllServices() {
        this.services.getServices(this.token).subscribe({
          next: (response) => {
            this.fetchedServices = response.filter((service: { category_name: string; }) =>
                !['Finance', 'Legal', 'Lifestyle'].includes(service.category_name)
            );
            
            this.filteredServices = [...this.fetchedServices];
            console.log('Filtered services:', this.fetchedServices);
          },
          error: (error) => {
            if (error.status === 404) {
                this.empty=true
                console.warn('No services found for this category.');
            } else {
                console.error('Error fetching services', error);
            }
          }
        });

      }

    NavigateToDetailsPage(listing: any) {
        this.router.navigate(['/listing-details'], {
            queryParams: {
                serviceCat: JSON.stringify(this.serviceCat),
                listing: JSON.stringify(listing)
            }
        });
    }
    
    getGradientClass(categoryName: string): string {
        if (!categoryName) {
            return 'default';
        }
        
        const categoryMap: {[key: string]: string} = {
            'Finance': 'finance',
            'Legal': 'legal',
            'Lifestyle': 'lifestyle',
            'Education': 'education',
            'Healthcare': 'healthcare',
            'Technology': 'technology',
            'Food': 'food',
            'Art': 'art',
            'Travel': 'travel'
        };
        
        if (categoryMap[categoryName]) {
            return categoryMap[categoryName];
        }
        
        const lowerCaseName = categoryName.toLowerCase();
        if (lowerCaseName.includes('tech') || lowerCaseName.includes('software') || lowerCaseName.includes('it')) {
            return 'technology';
        } else if (lowerCaseName.includes('food') || lowerCaseName.includes('cook') || lowerCaseName.includes('restaurant')) {
            return 'food';
        } else if (lowerCaseName.includes('health') || lowerCaseName.includes('medical') || lowerCaseName.includes('doctor')) {
            return 'healthcare';
        } else if (lowerCaseName.includes('art') || lowerCaseName.includes('design') || lowerCaseName.includes('creative')) {
            return 'art';
        } else if (lowerCaseName.includes('travel') || lowerCaseName.includes('tour') || lowerCaseName.includes('trip')) {
            return 'travel';
        } else if (lowerCaseName.includes('education') || lowerCaseName.includes('school') || lowerCaseName.includes('learn')) {
            return 'education';
        }
        
        return 'other';
    }
    
}
