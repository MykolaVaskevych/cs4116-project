import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonUtilsService} from '../../services/common-utils/common-utils.service';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import {FormsModule} from '@angular/forms';
import {Router} from '@angular/router';

@Component({
  selector: 'app-open-inquiry-window',
    imports: [
        FormsModule
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

    constructor(
        private commonUtilsService: CommonUtilsService,
        private inquiryService: InquiryService,
        private router: Router,
    ) {
        this.currentUser = this.commonUtilsService.getCurrentUser();
    }

    ngOnInit() {
        console.log(this.currentUser);
        console.log(this.listing)

        this.targetBusinessPersonnel = this.listing.business_name;
        this.targetBusinessName = this.listing.name;
    }

    closeModal() {
        this.responseEvent.emit({
            info: 'cancel',
            message: 'Modal Destroyed'
        });
    }

    inquire() {
        const inquiryData = {
            service: this.listing.id,
            subject: this.listing.name,
            initial_message: this.initial_message
        };

        this.inquiryService.createInquiry(inquiryData).subscribe((response: any) => {
            console.log(response);
            this.router.navigate(['/inquiry']);
        })

        this.responseEvent.emit({
            info: 'request',
        });
    }
}
