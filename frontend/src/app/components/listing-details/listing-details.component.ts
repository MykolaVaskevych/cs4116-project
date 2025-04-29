import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute } from '@angular/router';
import { ReviewsService } from '../../services/review-service/reviews.service';
import { NgbModal, NgbTooltip } from '@ng-bootstrap/ng-bootstrap';
import { OpenInquiryWindowComponent } from '../open-inquiry-window/open-inquiry-window.component';
import { ContactWithReviewerComponent } from '../contact-with-reviewer/contact-with-reviewer.component';
import { ReviewFormComponent } from '../review-form/review-form.component';
import { AuthService } from '../../services/auth-service/auth.service';
import { ServicesService } from '../../services/services-service/services.service';
import { ReportServiceComponent } from '../report-service/report-service.component';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';


@Component({
    selector: 'app-listing-details',
    standalone: true,
    imports: [CommonModule, NgbTooltip, MatDialogModule],
    templateUrl: './listing-details.component.html',
    styleUrl: './listing-details.component.css'
})
export class ListingDetailsComponent implements OnInit {
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
    
    currentUser: any
    userReview: any = null
    canReview: boolean = false

    constructor(
        private router: Router,
        private route: ActivatedRoute,
        private reviewsService: ReviewsService,
        private modalService: NgbModal,
        private authService: AuthService,
        private servicesService: ServicesService,
        private matDialog: MatDialog
    ) { }


    ngOnInit() {
        this.token = localStorage.getItem('access');
        this.currentUser = this.authService.getCurrentUser();
        console.log('token', this.token);
        console.log('currentUser', this.currentUser);

        this.route.queryParams.subscribe(params => {
            this.serviceCat = JSON.parse(params['serviceCat']);
            this.listing = JSON.parse(params['listing']);
            console.log('cat',this.serviceCat);
            console.log('listing',this.listing);
            
            // Check if user is a verified customer for this specific service
            if (this.currentUser && this.listing && this.listing.id && !this.currentUser.is_business) {
                this.servicesService.isVerifiedForService(this.token, this.listing.id).subscribe({
                    next: (response) => {
                        this.canReview = response.is_verified;
                        console.log('Can review:', this.canReview);
                    },
                    error: (error) => {
                        console.error('Error checking verification status:', error);
                        // Fallback: Check if user has a closed inquiry for this service
                        // This is handled on the backend side, but we'll provide a fallback for compatibility
                        this.canReview = this.currentUser?.is_verified_customer === true;
                        console.log('Fallback can review:', this.canReview);
                    },
                    complete: () => {
                        // Get reviews regardless of verification status
                        this.getReviews();
                    }
                });
            } else {
                // Business users can't review
                this.canReview = false;
                this.getReviews(); // Still get reviews to display
            }
        });
    }

    getReviews() {
        this.reviewsService.getReviews(this.token, this.listing.id).subscribe({
          next: (response) => {
            this.reviews = response;
            console.log('reviews', this.reviews);

            // Calculate average rating only if there are actual reviews
            if (this.reviews.length > 0) {
                this.avgRating = this.reviews.reduce((sum: any, review: { rating: any; }) => sum + review.rating, 0) / this.reviews.length;
                
                // Check if the current user has already left a review
                if (this.currentUser) {
                    this.userReview = this.reviews.find((review: any) => review.user === this.currentUser.id);
                }
            } else {
                // No reviews means no rating
                this.avgRating = 0;
            }

            console.log('avg rating', this.avgRating);
            console.log('userReview', this.userReview);
          },
          error: (error) => {
            console.error('Error fetching reviews', error);
            this.avgRating = 0;
          }
        });
      }
      
    openReviewForm() {
        const modalRef = this.modalService.open(ReviewFormComponent, { centered: true });
        modalRef.componentInstance.serviceId = this.listing.id;
        
        // If editing an existing review
        if (this.userReview) {
            modalRef.componentInstance.isEditing = true;
            modalRef.componentInstance.reviewId = this.userReview.review_id;
            modalRef.componentInstance.existingRating = this.userReview.rating;
            modalRef.componentInstance.existingComment = this.userReview.comment;
        }
        
        modalRef.componentInstance.reviewSubmitted.subscribe((reviewData: {rating: number, comment: string}) => {
            console.log('Review submitted:', reviewData);
            
            if (this.userReview) {
                // Update existing review
                this.reviewsService.updateReview(
                    this.token,
                    this.userReview.review_id,
                    reviewData.rating,
                    reviewData.comment
                ).subscribe({
                    next: (response) => {
                        console.log('Review updated:', response);
                        this.getReviews(); // Refresh reviews
                    },
                    error: (error) => {
                        console.error('Error updating review:', error);
                        alert('Failed to update your review. Please try again.');
                    }
                });
            } else {
                // Create new review
                this.reviewsService.createReview(
                    this.token,
                    this.listing.id,
                    reviewData.rating,
                    reviewData.comment
                ).subscribe({
                    next: (response) => {
                        console.log('Review created:', response);
                        this.getReviews(); // Refresh reviews
                    },
                    error: (error) => {
                        console.error('Error creating review:', error);
                        alert('Failed to submit your review. Please try again.');
                    }
                });
            }
        });
    }
    
    deleteReview() {
        if (!this.userReview) return;
        
        if (confirm('Are you sure you want to delete your review? This action cannot be undone.')) {
            this.reviewsService.deleteReview(this.token, this.userReview.review_id).subscribe({
                next: () => {
                    console.log('Review deleted');
                    this.userReview = null;
                    this.getReviews(); // Refresh reviews
                },
                error: (error) => {
                    console.error('Error deleting review:', error);
                    alert('Failed to delete your review. Please try again.');
                }
            });
        }
    }

    goBack() {
        this.router.navigate(['/service-listing'], {
            queryParams: {
                service: JSON.stringify(this.serviceCat)
            }
        });
    }

    openInquiryWindow() {
        const modalRef = this.modalService.open(OpenInquiryWindowComponent, { centered: true, scrollable: true });
        modalRef.componentInstance.listing = this.listing;

        // Listen for the response when modal is closed
        modalRef.componentInstance.responseEvent.subscribe((response: any) => {
            console.log(response);  // Handle the response from the modal
            modalRef.close();

            if (response.info === 'request') {

            }
        });
    }

    openContactWithReviewerForm(review: any): any {
        const modalRef = this.modalService.open(ContactWithReviewerComponent, { centered: true, scrollable: true });
        modalRef.componentInstance.review = review;

        // Listen for the response when modal is closed
        modalRef.componentInstance.responseEvent.subscribe((response: any) => {
            console.log(response);  // Handle the response from the modal

            if (response?.info === 'success' || response?.info === 'cancel') {
                modalRef.close();
            }
        });
    }
    
    openReportServiceForm(): void {
        const dialogRef = this.matDialog.open(ReportServiceComponent, {
            width: '500px',
            data: {
                serviceId: this.listing.id,
                serviceName: this.listing.business_name || 'Service Provider'
            },
            disableClose: false
        });

        dialogRef.afterClosed().subscribe(result => {
            console.log('Report dialog closed with result:', result);
            // If true, the report was submitted successfully
            if (result === true) {
                console.log('Service reported successfully');
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
