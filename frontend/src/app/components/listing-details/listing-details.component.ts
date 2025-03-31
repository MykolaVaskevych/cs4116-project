import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ReviewsService } from '../../services/review-service/reviews.service';


@Component({
    selector: 'app-listing-details',
    imports: [CommonModule],
    templateUrl: './listing-details.component.html',
    styleUrl: './listing-details.component.css'
})
export class ListingDetailsComponent {
    listing: any
    serviceCat: any
    token: any
    reviews: any
    avgRating = 0
    ratings= [
        { id: 1, desc: 'Scammer', score: 1.0 },
        { id: 2, desc: 'Best', score: 5.0 },
        { id: 3, desc: 'Meh', score: 2.1 }
    ]

    constructor(private router: Router, private route: ActivatedRoute, private reviewsService: ReviewsService) { }


    ngOnInit() {
        this.token =  localStorage.getItem('access');
        console.log('token', this.token)

        this.route.queryParams.subscribe(params => {
            this.serviceCat = JSON.parse(params['serviceCat']);
            this.listing = JSON.parse(params['listing']);
            console.log('cat',this.serviceCat); // access object properties
            console.log('listing',this.listing); // access object properties
        });

        this.getReviews()


    }

    getReviews() {
        this.reviewsService.getReviews(this.token, this.listing.id).subscribe({
          next: (response) => {
            this.reviews = response;
            console.log('reviews', this.reviews)

            if(this.reviews.length>0)
            this.avgRating = this.reviews.reduce((sum: any, review: { rating: any; }) => sum + review.rating, 0) / this.reviews.length;

        console.log('avg', this.avgRating)
          },
          error: (error) => {
            console.error('Error fetching profile', error);
          }
        });

      }

    goBack() {
        this.router.navigate(['/service-listing'], {
            queryParams: {
                service: JSON.stringify(this.serviceCat)
            }
        });
    }
}
