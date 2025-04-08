import {Component, EventEmitter, Input, Output} from '@angular/core';
import {NgbActiveModal} from '@ng-bootstrap/ng-bootstrap';
import {FormsModule} from '@angular/forms';

@Component({
    selector: 'app-request-payment',
    imports: [
        FormsModule
    ],
    templateUrl: './request-payment.component.html',
    styleUrl: './request-payment.component.css',
    providers: [NgbActiveModal]
})
export class RequestPaymentComponent {
    @Input() recipient: any;
    @Input() modalTitle: string = '';  // Input property for passing data
    @Input() modalMessage: string = '';  // Input property for passing data
    @Output() responseEvent: EventEmitter<any> = new EventEmitter();  // EventEmitter for passing data back to parent

    amount: any = 0;
    paymentMethod: any = 'wallet';
    message: any = '';

    constructor(public activeModal: NgbActiveModal) {}

    // This will be called when the modal is closed
    closeModal() {
        this.responseEvent.emit({
            info: 'cancel',
            message: 'Modal Destroyed'
        });
    }

    request() {
        this.responseEvent.emit({
            info: 'request',
            message: this.message,
            amount: this.amount,
        });
    }
}
