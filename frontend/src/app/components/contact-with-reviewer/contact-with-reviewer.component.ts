import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonUtilsService} from '../../services/common-utils/common-utils.service';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import {Router} from '@angular/router';
import {ConversationService} from '../../services/conversation-service/conversation.service';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-contact-with-reviewer',
    imports: [
        FormsModule,
        NgIf
    ],
  templateUrl: './contact-with-reviewer.component.html',
  styleUrl: './contact-with-reviewer.component.css'
})
export class ContactWithReviewerComponent implements OnInit {
    @Input() review: any;
    @Output() responseEvent: EventEmitter<any> = new EventEmitter();  // EventEmitter for passing data back to parent

    targetCustomerName: any;
    serviceName: any;
    currentUser: any;
    initial_message: any;
    ratingText: any;
    ratingPoint: any;
    agreementFlag = false;

    existingConversation = false;

    constructor(
        private commonUtilsService: CommonUtilsService,
        private router: Router,
        private conversationService: ConversationService,
    ) {
        this.currentUser = this.commonUtilsService.getCurrentUser();
    }

    ngOnInit() {
        console.log(this.currentUser);
        console.log(this.review)

        this.targetCustomerName = this.review.customer_name;
        this.serviceName = this.review.service_name;

        this.ratingText = this.review.comment;
        this.ratingPoint = this.review.rating;
    }

    closeModal() {
        this.responseEvent.emit({
            info: 'cancel',
            message: 'Modal Destroyed'
        });
    }

    contact() {
        const message = {
            recipient_id: this.review.user,
            initial_message: this.initial_message,
            review_id: this.review.review_id
        };

        this.conversationService.createConversationFromReview(message).subscribe((response: any) => {
            console.log(response);
            this.responseEvent.emit({
                info: 'success',
            });
            this.router.navigate(['/p2p']);
        }, error => {
            this.existingConversation = true;
            console.log(error);
        })
    }

    checkBoxClicked(): any {
        console.log('checkBoxClicked');
    }
}
