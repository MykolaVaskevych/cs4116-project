import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-payment-request-customer-view',
    imports: [
        ReactiveFormsModule,
        FormsModule,
        NgIf
    ],
  templateUrl: './payment-request-customer-view.component.html',
  styleUrl: './payment-request-customer-view.component.css',
    providers: [NgbActiveModal]
})
export class PaymentRequestCustomerViewComponent implements OnInit {
    @Input() paymentRequestUUID: string = '';
    @Output() responseEvent: EventEmitter<any> = new EventEmitter();  // EventEmitter for passing data back to parent
    updatedPaymentRequest: any;

    keepLoading = true;
    accept_reject = false;

    constructor(public inquiryService: InquiryService) {}

    ngOnInit(): void {
        // console.log(this.paymentRequestUUID);

        this.inquiryService.getPaymentRequestByUUID(this.paymentRequestUUID).subscribe(response => {
            console.log(response);
            this.updatedPaymentRequest = response;
            this.keepLoading = false;
        });
    }

    // This will be called when the modal is closed
    closeModal() {
        this.responseEvent.emit({
            info: 'cancel',
            message: 'Modal Destroyed'
        });
    }

    request(response: any) {
        this.accept_reject = true;
        this.inquiryService
            .acceptOrDeclinePaymentRequest(this.paymentRequestUUID, response)
            .subscribe(response => {
                this.accept_reject = false;
                this.responseEvent.emit({
                    info: 'request',
                });
        });
    }

    getDateString(date_data: any): any {
        const date = new Date(date_data);

        const formattedDate = date.toLocaleString('en-US', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            // hour: '2-digit',
            // minute: '2-digit',
            // second: '2-digit',
            hour12: true, // Use 24-hour clock
        });

        return formattedDate;
    }

    loadingAcceptReject(): any {
        const flag = this.accept_reject ? 'visible' : 'hidden';

        return `visibility: ${ flag }`;
    }
}
