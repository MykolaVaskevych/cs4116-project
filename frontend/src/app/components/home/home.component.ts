import { Component } from '@angular/core';
import { CommonModule, NgForOf, NgOptimizedImage, NgStyle } from '@angular/common';
import { Router } from '@angular/router';
import { ServicesService } from '../../services/services-service/services.service';


@Component({
    selector: 'app-banners',
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
        {
            id: 1, size: '600px',
            value: '',
            img: 'assets/banners/about_us.jpg',
            className: '',
        },
        {
            id: 2, size: '600px',
            value: `
                <div>
                    <h2>Urban Life Hub</h2>
                    <h5>We are a comprehensive platform designed to bridge the gap between customers and businesses in urban environments. We create meaningful connections that enhance urban living through seamless service delivery and community building. </h5>
                </div>
            `,
            className: 'inner-value-about-us-right',
        },  // Wider
        {
            id: 3, size: '600px',
            value: `
                <div>
<!--                    <h2>Our Origin</h2>-->
                    <h5>Urban Life Hub was created by Group 11 for the CS4116 project at the University of Limerick. Our team of dedicated developers combined their expertise in web development, user experience design, and business analytics to build this platform.</h5>
                </div>
            `,
            className: 'inner-value-about-us-bottom',
        },
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
        const allCategories = this.serviceCategories;
        
        this.router.navigate(['/service-listing'], { 
            queryParams: { 
                service: JSON.stringify(allCategories),
                filter: JSON.stringify({ 
                    category: Array.isArray(service) ? null : service.name,
                    isFromHome: true
                })
            }
        });
    }

    navigateToBlogs(): any {
        this.router.navigate(['/blogs']);
    }
}
