import {AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {NgClass, NgForOf, NgIf, NgOptimizedImage, NgStyle} from '@angular/common';
import {NgbModal, NgbPopover, NgbScrollSpy, NgbScrollSpyFragment, NgbTooltip} from '@ng-bootstrap/ng-bootstrap';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import {FormsModule} from '@angular/forms';
import Swal from 'sweetalert2';
import {CommonUtilsService} from '../../services/common-utils/common-utils.service';
import {RequestPaymentComponent} from '../request-payment/request-payment.component';
import {
    PaymentRequestCustomerViewComponent
} from '../payment-request-customer-view/payment-request-customer-view.component';

@Component({
  selector: 'app-inquiry',
    imports: [
        NgForOf,
        NgIf,
        FormsModule,
        NgbTooltip,
        NgbPopover,
    ],
  templateUrl: './inquiry.component.html',
  styleUrl: './inquiry.component.css'
})
export class InquiryComponent implements OnInit, AfterViewChecked, OnDestroy {
    @ViewChild('messageContainer') messageContainer!: ElementRef;

    randomUserList: any = [];
    inquiry_list: any = [];
    placeholder_dp = 'https://xsgames.co/randomusers/avatar.php?g=pixel';

    selectedRecipient: any;
    textMessages: any = [];
    currentInquiryOpenOrClosed: any = false;

    messageText: any = '';

    //  For the purpose of simulation
    dummy_textMessages = [
        {
            id: 1,
            user: 'User 1',
            text: 'Hey! How are you doing today?'
        },
        {
            id: 2,
            user: 'User 2',
            text: 'I’m good, thanks! Just been busy with work lately. What about you?'
        },
        {
            id: 3,
            user: 'User 1',
            text: 'I’ve been great, thanks for asking! Been working on some new projects. Really exciting stuff!'
        },
        {
            id: 4,
            user: 'User 2',
            text: 'That sounds interesting! What kind of projects are you working on?'
        },
        {
            id: 5,
            user: 'User 1',
            text: 'I’m working on a mobile app, actually. It’s going to be a game changer in the market! How about you, what’s keeping you busy?'
        },
        {
            id: 6,
            user: 'User 2',
            text: 'Nice, a mobile app sounds cool! I’ve been tied up with some meetings, but I’m also learning new stuff in the tech world. Always something new to learn!'
        },
        {
            id: 7,
            user: 'User 1',
            text: 'I know what you mean! The tech world moves fast. By the way, I started reading about quantum computing. It’s mind-blowing!'
        },
        {
            id: 8,
            user: 'User 2',
            text: 'Oh, I’ve heard of that! It sounds super complex, but also really cool. Do you think it’ll impact our daily lives anytime soon?'
        },
        {
            id: 9,
            user: 'User 1',
            text: 'Definitely, although it’s still in early stages. But once it matures, it’ll revolutionize industries like AI, security, and data processing!'
        },
        {
            id: 10,
            user: 'User 2',
            text: 'Wow, that’s impressive! I’ve been working more with AI lately too. The potential it has to automate tasks is amazing.'
        },
        {
            id: 11,
            user: 'User 1',
            text: 'Absolutely! It’s crazy how much AI can already do. I’ve been building some chatbots for a few projects, and the results are pretty amazing.'
        },
        {
            id: 12,
            user: 'User 2',
            text: 'I can imagine! I’ve been exploring NLP (Natural Language Processing) as well. It’s incredible how AI can understand and generate human language.'
        },
        {
            id: 13,
            user: 'User 1',
            text: 'NLP is a game-changer! Have you tried any of the latest frameworks? I’ve been playing around with GPT models.'
        },
        {
            id: 14,
            user: 'User 2',
            text: 'Yes! GPT-3 is amazing. The responses it generates are so human-like, sometimes it’s hard to tell it’s AI!'
        },
        {
            id: 15,
            user: 'User 1',
            text: 'Right?! It’s wild how advanced it’s getting. We’re on the brink of some serious breakthroughs in AI!'
        },
        {
            id: 16,
            user: 'User 2',
            text: 'For sure! It feels like we’re living in the future already. What else have you been learning lately?'
        },
        {
            id: 17,
            user: 'User 1',
            text: 'Lately, I’ve been diving into cybersecurity. With everything moving online, I think it’s crucial to understand how to protect data.'
        },
        {
            id: 18,
            user: 'User 2',
            text: 'That’s really important. Cybersecurity is becoming more of a priority for businesses. Are you working on any cybersecurity projects?'
        },
        {
            id: 19,
            user: 'User 1',
            text: 'Yes, actually! I’m building a security system for IoT devices. It’s a challenge, but I’m enjoying it.'
        },
        {
            id: 20,
            user: 'User 2',
            text: 'That’s amazing! IoT security is such a big issue right now. It must be rewarding to work on something so important.'
        },
        {
            id: 21,
            user: 'User 1',
            text: 'It really is. And the best part is that I’m learning so much along the way. What’s your next project about?'
        },
        {
            id: 22,
            user: 'User 2',
            text: 'I’m currently building a recommendation engine using machine learning. It’s challenging, but I love the problem-solving aspect of it.'
        },
        {
            id: 23,
            user: 'User 1',
            text: 'That’s awesome! Recommendation systems are everywhere these days. Have you implemented any advanced techniques like collaborative filtering?'
        },
        {
            id: 24,
            user: 'User 2',
            text: 'Yes, I’ve been experimenting with collaborative filtering, and it’s really impressive how much it improves the accuracy of recommendations!'
        },
        {
            id: 25,
            user: 'User 1',
            text: 'It’s a game-changer! The more personalized the recommendation, the better the user experience. It’s great that you’re exploring that!'
        }
    ];

    additionalHeightUnderMessages = [
        { id: 'A1' },
        { id: 'A2' },
        { id: 'A3' },
    ];

    timeoutId: any;
    timeoutId_PaymentRequest: any;
    shouldScrollToBottom = false;

    inputFiledVisibilityFlag = false;
    paymentRequestSent = false;
    paymentRequestReceived = false;
    paymentRequestReceivedText = '';
    paymentRequestSentText = '';

    lastAcceptedOrDeclinedRequest!: boolean;
    lastAcceptedOrDeclinedRequestText = '';

    activePaymentRequest: any;

    constructor(
        private inquiryService: InquiryService,
        private commonUtilsService: CommonUtilsService,
        private modalService: NgbModal
    ) {
    }

    ngOnDestroy(): void {
        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }
    }

    ngOnInit() {
        this.inquiryService.getAllInquiries().subscribe(response => {
            // console.log(response);
            response
                // @ts-ignore
                .sort((a: any, b: any) => new Date(b.updated_at) - new Date(a.updated_at))
                // .filter((item: any) => item.status === 'OPEN')
                .map((item: any) => {
                    this.inquiry_list.push(item);
            });
            this.selectedRecipient = this.inquiry_list[0];
            this.startPolling(this.selectedRecipient);
            this.inputFiledVisibilityFlag = true;
            // this.viewPaymentRequest();
            // this.textMessages = response[0].messages;
            // this.currentInquiryOpenOrClosed = (response[0].status === 'CLOSED');
            // console.log(this.currentInquiryOpenOrClosed);
        })
    }

    ngAfterViewChecked() {
        if (this.shouldScrollToBottom) {
            // console.log("SCROLLING DOWN....")
            this.scrollToBottom();
            this.shouldScrollToBottom = false;
        }
    }

    scrollToBottom() {
        try {
            // Scroll the message container to the bottom
            this.messageContainer.nativeElement.scrollTop = this.messageContainer.nativeElement.scrollHeight;
        } catch (err) {
            console.error('Error scrolling to bottom:', err);
        }
    }

    getInquiryName(inquiry: any): any {
        const current_user = this.commonUtilsService.getCurrentUser();
        // console.log(current_user);

        if (!inquiry) {
            return;
        }

        if (current_user.role === 'CUSTOMER') {
            return inquiry.business_name;
        } else {
            return inquiry.customer_name;
        }
    }

    getFullName(inquiry: any): any {
        return inquiry.customer_name;

        // let nameObject = user.name;
        // return nameObject.title + ' ' + nameObject.first + ' ' + nameObject.last;
    }

    getSingleMessageClass(message: any): any {
        // console.log(message);
        const current_user = this.commonUtilsService.getCurrentUser();
        if (current_user.role === 'CUSTOMER') {
            if (message.sender_role.toLowerCase() === 'customer') {
                return 'right';
            } else {
                return 'left';
            }
        } else {
            if (message.sender_role.toLowerCase() === 'customer') {
                return 'left';
            } else {
                return 'right';
            }
        }

        // return `${message.sender_role.toLowerCase() === 'customer' ? 'left' : 'right' }`;

        // return '';
    }

    startPolling(user: any): any {
        let isFirstLoad = true;
        // console.log(user);
        this.selectedRecipient = user;
        this.lastAcceptedOrDeclinedRequest = false;

        this.messageText = '';
        this.currentInquiryOpenOrClosed = (user.status === 'CLOSED');
        // console.log(this.currentInquiryOpenOrClosed);
        // this.textMessages = user.messages;

        let isRefreshing = false;

        if (this.timeoutId) {
            clearTimeout(this.timeoutId);
        }

        let lookForData_PaymentRequest = () => {
            let subscription = this.inquiryService.getPaymentRequest().subscribe(response => {
                this.lastAcceptedOrDeclinedRequest = false;
                response = response.filter((item: any) => item.inquiry === this.selectedRecipient.id);

                let filteredData = response
                    .filter((item: any) => item.status === 'PENDING')
                    .find((item: any) => item.inquiry === this.selectedRecipient.id);

                // console.log(this.commonUtilsService.getCurrentUser());
                // console.log(this.selectedRecipient.id);

                if (filteredData?.status === 'PENDING') {
                    this.activePaymentRequest = filteredData;
                    // console.log('PENDING FOUND')
                    this.paymentRequestSent = (
                        this.commonUtilsService.getCurrentUser().is_business === true ||
                        this.commonUtilsService.getCurrentUser().is_moderator === true
                    );
                    this.paymentRequestSentText = `Payment Request sent. Amount: ${filteredData.amount}`;

                    this.paymentRequestReceived = (
                        this.commonUtilsService.getCurrentUser().is_business === false &&
                        this.commonUtilsService.getCurrentUser().is_moderator === false
                    );
                    this.paymentRequestReceivedText = `New Payment Request Received.`;
                } else {
                    console.log('NO PENDING');

                    if (response.length !== 0) {
                        // @ts-ignore
                        response.sort((a: any, b: any) => a.id - b.id);

                        const temp_object = response[response.length - 1];
                        // @ts-ignore
                        this.lastAcceptedOrDeclinedRequest = true;
                        this.lastAcceptedOrDeclinedRequestText = `The last payment request was ${temp_object.status}`;

                        console.log(this.lastAcceptedOrDeclinedRequest);
                    }

                    this.paymentRequestSent = false;
                    this.paymentRequestReceived = false;
                }

                this.timeoutId_PaymentRequest = setTimeout(() => {
                    subscription.unsubscribe();
                    lookForData_PaymentRequest();
                }, 2000);
            });
        }

        let lookForData = () => {
            let subscription = this.inquiryService.getInquiryMessage(user.id).subscribe(response => {
                // console.log(response);
                this.textMessages = response;

                if (isFirstLoad) {
                    setTimeout(() => {
                        this.shouldScrollToBottom = true;
                        isFirstLoad = false;
                    }, 50);
                }

                this.timeoutId = setTimeout(() => {
                    subscription.unsubscribe(); // Stop previous API call
                    lookForData(); // Call again
                }, 2000);
            }, error => {
                console.error(error);
                if (error.status === 401) {
                    this.commonUtilsService.showSessionExpired()
                        .then((result) => {
                            window.location.reload();
                        });
                }
            });
        };

        lookForData(); // Start the polling
        lookForData_PaymentRequest(); // Start the polling
    }

    sendMessage() {
        console.log(this.messageText);
        console.log(this.selectedRecipient);
        console.log(this.textMessages)

        this.inquiryService.sendInquiryMessage(this.messageText, this.selectedRecipient.id).subscribe(response => {
            console.log(response);
            this.textMessages.push(response);
            this.messageText = '';
        }, err => {
            Swal.fire({
                icon: "error",
                position: "top-end",
                showConfirmButton: false,
                timer: 1500,
                timerProgressBar: true,
                title: "Message Failed!",
            });
        })
    }

    getShouldBeDisabled() {
        return this.currentInquiryOpenOrClosed ? 'disable-input' : '';
    }

    markAsVisibleInquiry(inquiry: any) {
        const opacityValue = this.selectedRecipient.id === inquiry.id ? 1 : 0;
        return `opacity: ${opacityValue}`;
    }

    isClosedInquiry(inquiry: any) {
        let isClosed = inquiry.status === 'CLOSED' ? 1 : 0;

        return `opacity: ${isClosed}`;
    }

    showInquiryCloseButton(inquiry: any) {
        let isClosed = inquiry.status === 'CLOSED' ? 0 : 1;
        const current_user = this.commonUtilsService.getCurrentUser();
        if (current_user.role !== 'MODERATOR') {
            isClosed = 0;
        }

        return `opacity: ${isClosed}`;
    }

    acceptClose(p: any) {
        this.inquiryService.closeInquiry(this.selectedRecipient.id).subscribe(response => {
            // First, get updated inquiry
            this.inquiryService.getSingleInquiry(this.selectedRecipient.id).subscribe(response => {
                console.log(response);

                this.inquiry_list = this.inquiry_list.map((inquiry: any) => {
                    if (inquiry.id === response.id) {
                        return { ...inquiry, ...response };
                    }
                    return inquiry;
                });
                this.selectedRecipient = response;
                this.currentInquiryOpenOrClosed = (this.selectedRecipient.status === 'CLOSED');
                
                // Get service ID for this inquiry to verify the customer
                if (response.status === 'CLOSED') {
                    this.inquiryService.getInquiryServiceId(this.selectedRecipient.id).subscribe(
                        serviceData => {
                            if (serviceData && serviceData.service_id) {
                                console.log('Customer verified for service ID:', serviceData.service_id);
                                console.log('Is customer verified:', serviceData.is_verified);
                                // The backend handles adding the customer to verified customers list
                                // Show a success message
                                Swal.fire({
                                    icon: "success",
                                    position: "top-end",
                                    showConfirmButton: false,
                                    timer: 2000,
                                    timerProgressBar: true,
                                    title: "Inquiry closed!",
                                    text: "Customer can now leave reviews for this service."
                                });
                            }
                        },
                        error => {
                            console.error('Error getting service ID for inquiry:', error);
                        }
                    );
                }
            });
        });

        p.close();
    }

    rejectClose(p: any) {
        p.close();
    }

    openRequestPaymentView() {
        const modalRef = this.modalService.open(RequestPaymentComponent, { centered: true });
        modalRef.componentInstance.recipient = this.selectedRecipient;
        modalRef.componentInstance.modalTitle = 'Modal Title';  // Pass data into the modal
        modalRef.componentInstance.modalMessage = 'This is the content of the modal';  // Pass more data

        // Listen for the response when modal is closed
        modalRef.componentInstance.responseEvent.subscribe((response: any) => {
            console.log(response);  // Handle the response from the modal
            modalRef.close();

            if (response.info === 'request') {
                const payload = {
                    inquiry: this.selectedRecipient.id,
                    description: response.message,
                    amount: response.amount
                }

                this.inquiryService.createPaymentRequest(payload).subscribe(response => {
                    console.log(response);
                });
            }
        });
    }

    viewPaymentRequest() {
        const modalRef = this.modalService.open(PaymentRequestCustomerViewComponent, { centered: true });
        modalRef.componentInstance.paymentRequestUUID = this.activePaymentRequest.request_id;
        modalRef.componentInstance.modalTitle = 'Modal Title';  // Pass data into the modal
        modalRef.componentInstance.modalMessage = 'This is the content of the modal';  // Pass more data

        // Listen for the response when modal is closed
        modalRef.componentInstance.responseEvent.subscribe((response: any) => {
            console.log(response);  // Handle the response from the modal
            modalRef.close();
            
            // Handle error responses
            if (response.info === 'error') {
                Swal.fire({
                    icon: "error",
                    position: "top-end",
                    showConfirmButton: true,
                    title: "Payment Error",
                    text: response.message
                });
            } else if (response.info === 'request' && response.success) {
                Swal.fire({
                    icon: "success",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 1500,
                    timerProgressBar: true,
                    title: "Payment Request Processed",
                    text: response.message
                });
            }
        });
    }

    shouldRequestPaymentButtonBeVisible() {
        let visibility = true;
        const current_user = this.commonUtilsService.getCurrentUser();
        if (current_user.role == 'CUSTOMER') {
            visibility = false;
        }

        return visibility;
    }

}
