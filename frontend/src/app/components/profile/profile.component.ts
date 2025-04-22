import { Component, HostListener } from '@angular/core';
import {FormGroup, FormControl, Validators, FormBuilder, FormsModule} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth-service/auth.service';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { UserProfileService } from '../../services/user-profile.service';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';

interface Transaction {
  type: string;
  amount: number;
  date: string;
  icon: string;
}

@Component({
    selector: 'app-profile',
    imports: [CommonModule, ReactiveFormsModule, FormsModule],
    templateUrl: './profile.component.html',
    styleUrl: './profile.component.css',
})
export class ProfileComponent {
    activeSection = 'personal'; // Default active section
    isProvider = false;
    loginForm!: FormGroup;
    passwordForm!: FormGroup;
    businessForm!: FormGroup;
    errorListAfterSignUp = [];
    passwordFormError = false;
    businessFormError = false;
    applyStyle = false;
    user: any;
    token: any;

    depositSelectionFlag = false;
    withdrawSelectionFlag = false;
    transferSelectionFlag = false;

    depositError = false;
    depositErrorText = '';

    transferError = false;
    transferErrorText = '';

    walletAmount = 0;
    depositAmount = 0;
    withdrawAmount = 0;
    transferAmount = 0;

    transferRecipient = '';
    transactions: Transaction[] = [];

    @HostListener('window:resize', ['$event'])
    onResize(event: any) {
        this.applyStyle = window.innerWidth < 1200 && !this.isProvider;
    }

    constructor(
        private fb: FormBuilder, 
        private router: Router, 
        private authService: AuthService,
        private userProfileService: UserProfileService, 
        private inquiryService: InquiryService
    ) { }

    ngOnInit() {
        this.token = localStorage.getItem('access');
        console.log('token', this.token);

        this.isProvider = JSON.parse(localStorage.getItem('isProvider') || 'false');
        console.log('isporovider', this.isProvider);

        this.loginForm = new FormGroup({
            email: new FormControl(''),
            password: new FormControl(''),
        });

        this.passwordForm = this.fb.group({
            oldPassword: ['', Validators.required],
            newPassword: ['', Validators.required]
        });

        this.businessForm = this.fb.group({
            fullName: ['', Validators.required],
            businessInfo: ['', Validators.required]
        });
        
        this.onResize(null);
        this.loadUserProfile();
        this.updateWalletAmount();
    }

    loadUserProfile() {
        this.userProfileService.getProfile(this.token).subscribe({
          next: (response) => {
            this.user = response;
            console.log('user', this.user);
          },
          error: (error) => {
            console.error('Error fetching profile', error);
          }
        });
    }

    onSubmitBusinessForm() {
        if (this.businessForm.invalid) {
            this.businessForm.markAllAsTouched();
            this.businessFormError = true;
            return;
        } else {
            this.businessFormError = false;
            const fullName = this.businessForm.value.fullName;
            const businessInfo = this.businessForm.value.businessInfo;

            const obj = {
                fullName: fullName,
                businessInfo: businessInfo
            };

            console.log('Filled form:', obj);
            this.makeProvider();
        }
    }

    logInButton(event: Event): void {
        event.preventDefault();
        this.errorListAfterSignUp = [];

        this.authService.login({
            email: this.loginForm.value.email,
            password: this.loginForm.value.password
        }).subscribe(result => {
            console.log(result.access);
            localStorage.setItem('access', result.access);

            this.router.navigate(['home']);
        }, error => {
            console.log(error);

            Object.values(error.error).forEach(message => {
                // @ts-ignore
                this.errorListAfterSignUp.push(message);
            });
        });
    }

    onUpdatePassword() {
        if (this.passwordForm.valid) {
            this.passwordFormError = false;
            const oldPass = this.passwordForm.value.oldPassword;
            const newPass = this.passwordForm.value.newPassword;

            console.log('Old Password:', oldPass);
            console.log('New Password:', newPass);
            // TODO: Call backend API here
        } else {
            console.log('Form Invalid');
            this.businessForm.markAllAsTouched();
            this.passwordFormError = true;
        }
    }

    makeProvider() {
        const updatedData = { role: 'BUSINESS' };

        this.userProfileService.updateProfile(this.token, updatedData).subscribe({
          next: (response) => {
            console.log('Role updated successfully', response);
            localStorage.setItem('isProvider', JSON.stringify(true));
            this.isProvider = true;
            console.log(this.isProvider, 'isprovider');
            this.loadUserProfile(); // Refresh user data after updating
          },
          error: (error) => {
            console.error('Error updating role', error);
          }
        });
    }

    walletDeposit(): any {
        this.depositError = false;
        this.inquiryService.walletDeposit(this.depositAmount).subscribe(result => {
            console.log(result);
            
            // Add to transaction history
            this.addTransaction('Deposit', this.depositAmount, 'fa fa-arrow-down');
            
            this.depositAmount = 0;
            this.walletAmount = result.new_balance;
            
            // Close the form
            this.closeWalletForms();
        }, error => {
            this.depositError = true;
        });
    }

    walletWithdraw(): any {
        this.depositError = false;
        this.inquiryService.walletWithdraw(this.withdrawAmount).subscribe(result => {
            console.log(result);
            
            // Add to transaction history
            this.addTransaction('Withdrawal', -this.withdrawAmount, 'fa fa-arrow-up');
            
            this.withdrawAmount = 0;
            this.walletAmount = result.new_balance;
            
            // Close the form
            this.closeWalletForms();
        }, error => {
            this.depositError = true;
        });
    }

    walletTransfer(): any {
        this.transferError = false;
        this.depositError = false;
        this.inquiryService.walletTransfer(this.transferAmount, this.transferRecipient).subscribe(result => {
            console.log(result);
            
            // Add to transaction history
            this.addTransaction('Transfer to ' + this.transferRecipient, -this.transferAmount, 'fa fa-exchange-alt');
            
            this.transferAmount = 0;
            this.transferRecipient = '';
            this.walletAmount = result.new_balance;
            
            // Close the form
            this.closeWalletForms();
        }, error => {
            this.transferError = true;
            this.transferErrorText = error.error.error || error.error.recipient_email || error.error.amount;
            console.log(error.error);
        });
    }

    updateWalletAmount(): any {
        this.inquiryService.getWallet().subscribe(response => {
            this.walletAmount = response.balance;
        });
    }

    toggleWalletAction(action: string): void {
        console.log(`Selection: ${action}`);
        if (action === 'deposit') {
            this.depositSelectionFlag = !this.depositSelectionFlag;
            this.withdrawSelectionFlag = false;
            this.transferSelectionFlag = false;
        } else if (action === 'withdraw') {
            this.withdrawSelectionFlag = !this.withdrawSelectionFlag;
            this.depositSelectionFlag = false;
            this.transferSelectionFlag = false;
        } else if (action === 'transfer') {
            this.transferSelectionFlag = !this.transferSelectionFlag;
            this.depositSelectionFlag = false;
            this.withdrawSelectionFlag = false;
        }
    }
    
    closeWalletForms(): void {
        this.depositSelectionFlag = false;
        this.withdrawSelectionFlag = false;
        this.transferSelectionFlag = false;
    }
    
    addTransaction(type: string, amount: number, icon: string): void {
        const now = new Date();
        const transaction: Transaction = {
            type: type,
            amount: amount,
            date: now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            icon: icon
        };
        
        // Add to beginning of array
        this.transactions.unshift(transaction);
    }
}
