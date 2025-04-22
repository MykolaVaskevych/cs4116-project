import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonUtilsService} from '../../services/common-utils/common-utils.service';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import {FormsModule} from '@angular/forms';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-open-inquiry-window',
    imports: [
        FormsModule,
        CommonModule
    ],
  templateUrl: './open-inquiry-window.component.html',
  styleUrl: './open-inquiry-window.component.css'
})
export class OpenInquiryWindowComponent implements OnInit {
    @Input() listing: any;
    @Output() responseEvent: EventEmitter<any> = new EventEmitter();  // EventEmitter for passing data back to parent

    targetBusinessPersonnel: any;
    targetBusinessName: any;
    currentUser: any;
    initial_message: any;
    servicePrice: number = 0;
    hasPrice: boolean = false;
    walletBalance: number = 0;
    hasEnoughFunds: boolean = true;

    constructor(
        private commonUtilsService: CommonUtilsService,
        private inquiryService: InquiryService,
        private router: Router,
    ) {
        this.currentUser = this.commonUtilsService.getCurrentUser();
    }

    ngOnInit() {
        console.log(this.currentUser);
        console.log(this.listing);

        this.targetBusinessPersonnel = this.listing.business_name;
        this.targetBusinessName = this.listing.name;
        
        // Check if service has a fixed price
        if (this.listing.fixed_price && parseFloat(this.listing.fixed_price) > 0) {
            this.servicePrice = parseFloat(this.listing.fixed_price);
            this.hasPrice = true;
            
            // Get wallet balance
            this.inquiryService.getWallet().subscribe({
                next: (wallet: any) => {
                    this.walletBalance = parseFloat(wallet.balance);
                    this.hasEnoughFunds = this.walletBalance >= this.servicePrice;
                },
                error: (error: any) => {
                    console.error('Error fetching wallet:', error);
                }
            });
        }
    }

    closeModal() {
        this.responseEvent.emit({
            info: 'cancel',
            message: 'Modal Destroyed'
        });
    }

    inquire() {
        // First check if user has enough funds for paid service
        if (this.hasPrice && !this.hasEnoughFunds) {
            // Show alert about insufficient funds
            alert('You do not have enough funds to open this inquiry. Please deposit more funds.');
            return;
        }

        const inquiryData = {
            service: this.listing.id,
            subject: this.listing.name,
            initial_message: this.initial_message
        };

        this.inquiryService.createInquiry(inquiryData).subscribe({
            next: (response: any) => {
                console.log(response);
                this.router.navigate(['/inquiry']);
                
                // If this was a paid inquiry, show a confirmation message
                if (this.hasPrice) {
                    alert(`Successfully created inquiry. €${this.servicePrice.toFixed(2)} has been transferred to the service provider.`);
                }
            },
            error: (error: any) => {
                console.error('Error creating inquiry:', error);
                
                // Handle specific errors
                if (error.status === 400 && error.error?.detail === 'Insufficient funds' || (error.error && typeof error.error === 'string' && error.error.includes('Insufficient funds'))) {
                    alert('Insufficient funds to open this inquiry. Please deposit more funds.');
                } else {
                    alert('Failed to create inquiry. Please try again.');
                }
            }
        });

        this.responseEvent.emit({
            info: 'request',
        });
    }
}