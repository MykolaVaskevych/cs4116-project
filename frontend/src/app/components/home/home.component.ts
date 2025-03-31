import { Component } from '@angular/core';
import { CommonModule, NgForOf, NgOptimizedImage, NgStyle } from '@angular/common';
import { Router } from '@angular/router';
import { ServicesService } from '../../services/services-service/services.service';


@Component({
    selector: 'app-home',
    imports: [
        NgForOf,
        NgStyle,
        CommonModule
    ],
    templateUrl: './home.component.html',
    styleUrl: './home.component.css'
})
export class HomeComponent {
    serviceCategories: any
    token: any
    filteredCategories: any
    hasOtherCategories: any
    otherCategories: any

    constructor(private router: Router, private services: ServicesService) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        console.log('token', this.token);


        this.getServiceCategories()
    }

    aboutUsItems = [
        { id: 1, size: '600px', value: '' },
        { id: 2, size: '600px', value: '' },  // Wider
        { id: 3, size: '600px', value: '' },
    ];



    getServiceCategories() {
        this.services.getServiceCategories(this.token).subscribe({
            next: (response) => {
                this.serviceCategories = response;
                console.log('service cats', this.serviceCategories)

                this.filteredCategories = this.serviceCategories.filter((service: { name: string; }) =>
                    ['Legal', 'Finance', 'Lifestyle'].includes(service.name)
                  );

                  this.hasOtherCategories = this.serviceCategories.some((service: { name: string; }) =>
                    !['Legal', 'Finance', 'Lifestyle'].includes(service.name)
                  );

                  this.otherCategories = this.serviceCategories.filter((s: { name: string; }) =>
                    !['Legal', 'Finance', 'Lifestyle'].includes(s.name)
                );

            },
            error: (error) => {
                console.error('Error fetching cats', error);
            }
        });

    }

    NavigateToServiceListing(service: any) {
        this.router.navigate(['/service-listing'], { queryParams: { service: JSON.stringify(service)  } });
    }
}
