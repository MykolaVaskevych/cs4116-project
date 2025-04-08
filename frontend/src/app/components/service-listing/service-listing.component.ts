import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ServicesService } from '../../services/services-service/services.service';
import { FormsModule } from '@angular/forms';
import { filter } from 'rxjs';


@Component({
    selector: 'app-service-listing',
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

    constructor(private router: Router, private route: ActivatedRoute, private services: ServicesService
    ) { }

    ngOnInit() {
        console.log('searchterm', this.searchTerm)
        this.token =  localStorage.getItem('access');
        console.log('token', this.token)

        this.route.queryParams.subscribe(params => {
            this.serviceCat = JSON.parse(params['service']);
            console.log('serviceCat received:', this.serviceCat);

            if(this.serviceCat.length>1){
                console.log('other cats')
                this.other=true
                this.getAllServices()
            }
            else{
                this.getServicesByCategories()
            }
        });

        this.isProvider = JSON.parse(localStorage.getItem('isProvider') || 'false');
        console.log(this.isProvider, 'isprovider');
    }

    redirectToCreateListing(){
        this.router.navigate(['/create-listing'], {
            queryParams: {
                serviceCat: JSON.stringify(this.serviceCat)
            }
        });
    }

    filterServices() {
        this.filteredServices = this.fetchedServices.filter((service: { description: string; }) =>
          service.description.toLowerCase().includes(this.searchTerm.toLowerCase())
        );

        console.log('filtered', this.filteredServices)
      }

      getServicesByCategories() {
        this.services.getServicesByCategories(this.token, this.serviceCat.id).subscribe({
          next: (response) => {
            this.fetchedServices = response;
            this.filteredServices = [...this.fetchedServices];
            console.log('services', this.fetchedServices)
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
}
