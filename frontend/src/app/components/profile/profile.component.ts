import { Component, HostListener, ViewChild, ElementRef } from '@angular/core';
import {FormGroup, FormControl, Validators, FormBuilder, FormsModule} from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth-service/auth.service';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { UserProfileService } from '../../services/user-profile.service';
import {InquiryService} from '../../services/inquiry-service/inquiry.service';
import { environment } from '../../../env/environment';

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
    @ViewChild('fileInput') fileInput!: ElementRef;
    
    activeSection = 'personal'; // Default active section
    isProvider = false;
    loginForm!: FormGroup;
    passwordForm!: FormGroup;
    profileForm!: FormGroup;
    businessForm!: FormGroup;
    errorListAfterSignUp = [];
    passwordFormError = false;
    passwordErrorText = '';
    passwordUpdateSuccess = false;
    profileFormError = false;
    businessFormError = false;
    applyStyle = false;
    isEditingProfile = false;
    user: any;
    token: any;
    profileImage: string | null = null;
    photoUploadError: string | null = null;
    
    // Photo upload modal
    showPhotoModal = false;
    selectedImage: File | null = null;
    imagePreviewSrc: string | null = null;
    isUploading = false;
    
    // Password visibility toggle
    showPasswords = false;

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

        // Password form with validation
        this.passwordForm = this.fb.group({
            old_password: ['', Validators.required],
            new_password: ['', [Validators.required, Validators.minLength(8)]],
            confirm_password: ['', Validators.required]
        }, { validators: this.passwordMatchValidator });

        // Profile form
        this.profileForm = this.fb.group({
            username: ['', Validators.required],
            email: [{value: '', disabled: true}],
            first_name: [''],
            last_name: ['']
        });

        this.businessForm = this.fb.group({
            fullName: ['', Validators.required],
            businessInfo: ['', Validators.required]
        });
        
        this.onResize(null);
        this.loadUserProfile();
        this.updateWalletAmount();
    }
    
    // Custom validator to check if passwords match
    passwordMatchValidator(formGroup: FormGroup) {
        const newPassword = formGroup.get('new_password')?.value;
        const confirmPassword = formGroup.get('confirm_password')?.value;
        
        if (newPassword !== confirmPassword) {
            return { passwordMismatch: true };
        }
        
        return null;
    }

    loadUserProfile() {
        this.userProfileService.getProfile(this.token).subscribe({
          next: (response) => {
            this.user = response;
            console.log('user', this.user);
            
            // Initialize profile form with current user data
            this.profileForm.patchValue({
              username: this.user.username || '',
              email: this.user.email || '',
              first_name: this.user.first_name || '',
              last_name: this.user.last_name || ''
            });
            
            // Set profile image if available
            if (this.user.profile_image) {
              this.profileImage = `${environment.apiHost}${this.user.profile_image}`;
            }
          },
          error: (error) => {
            console.error('Error fetching profile', error);
          }
        });
    }
    
    // Open the photo upload modal
    openPhotoModal() {
      this.showPhotoModal = true;
      this.photoUploadError = null;
      this.selectedImage = null;
      this.imagePreviewSrc = null;
    }
    
    // Close the photo upload modal
    closePhotoModal() {
      this.showPhotoModal = false;
    }
    
    // Trigger file input click when button is clicked
    triggerFileInput() {
      this.fileInput.nativeElement.click();
    }
    
    // Handle image selection
    onImageSelected(event: Event) {
      const element = event.target as HTMLInputElement;
      if (element.files && element.files.length) {
        const file = element.files[0];
        
        // Check if file is an image
        if (!file.type.includes('image')) {
          this.photoUploadError = 'Please select an image file.';
          return;
        }
        
        // Check file size (limit to 2MB)
        if (file.size > 2 * 1024 * 1024) {
          this.photoUploadError = 'Image must be less than 2MB.';
          return;
        }
        
        // Reset error
        this.photoUploadError = null;
        this.selectedImage = file;
        
        // Create preview
        const reader = new FileReader();
        reader.onload = () => {
          this.imagePreviewSrc = reader.result as string;
        };
        reader.readAsDataURL(file);
      }
    }
    
    // Remove selected image
    removeSelectedImage() {
      this.selectedImage = null;
      this.imagePreviewSrc = null;
      this.fileInput.nativeElement.value = '';
    }
    
    // Upload the profile image
    uploadProfileImage() {
      if (!this.selectedImage) {
        return;
      }
      
      this.isUploading = true;
      this.photoUploadError = null;
      
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('profile_image', this.selectedImage, this.selectedImage.name);
      
      // Upload profile image using the dedicated method
      this.userProfileService.updateProfileImage(this.token, formData).subscribe({
        next: (response: any) => {
          console.log('Profile image updated successfully', response);
          
          // Update the profile image
          if (response.profile_image) {
            this.profileImage = `${environment.apiHost}${response.profile_image}`;
          } else {
            // If no URL is returned in the response, use the preview as fallback
            this.profileImage = this.imagePreviewSrc;
          }
          
          // Close the modal
          this.showPhotoModal = false;
          this.isUploading = false;
          
          // Reset the form
          this.selectedImage = null;
          this.imagePreviewSrc = null;
        },
        error: (error: any) => {
          console.error('Error updating profile image', error);
          this.photoUploadError = 'Failed to upload image. Please try again.';
          this.isUploading = false;
        }
      });
    }
    
    // Start editing profile
    editProfile() {
        this.isEditingProfile = true;
    }
    
    // Cancel profile editing
    cancelEditProfile() {
        this.isEditingProfile = false;
        this.profileFormError = false;
        
        // Reset the form to current user data
        this.profileForm.patchValue({
          username: this.user.username || '',
          email: this.user.email || '',
          first_name: this.user.first_name || '',
          last_name: this.user.last_name || ''
        });
    }
    
    // Save profile changes
    onUpdateProfile() {
        if (this.profileForm.valid) {
            this.profileFormError = false;
            
            const updatedData = {
                username: this.profileForm.value.username,
                first_name: this.profileForm.value.first_name,
                last_name: this.profileForm.value.last_name
            };
            
            this.userProfileService.updateProfile(this.token, updatedData).subscribe({
                next: (response) => {
                    this.user = response;
                    this.isEditingProfile = false;
                    console.log('Profile updated successfully', response);
                },
                error: (error) => {
                    this.profileFormError = true;
                    console.error('Error updating profile', error);
                }
            });
        } else {
            this.profileFormError = true;
            this.profileForm.markAllAsTouched();
        }
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
            this.passwordUpdateSuccess = false;
            
            const passwordData = {
                old_password: this.passwordForm.value.old_password,
                new_password: this.passwordForm.value.new_password,
                confirm_password: this.passwordForm.value.confirm_password
            };
            
            console.log('Submitting password data:', passwordData);
            
            this.userProfileService.updatePassword(this.token, passwordData).subscribe({
                next: (response) => {
                    console.log('Password updated successfully', response);
                    this.passwordUpdateSuccess = true;
                    this.passwordForm.reset();
                },
                error: (error) => {
                    this.passwordFormError = true;
                    console.error('Error changing password', error);
                    
                    if (error.error && typeof error.error === 'object') {
                        // Handle error messages from backend
                        if (error.error.old_password) {
                            this.passwordErrorText = error.error.old_password;
                        } else if (error.error.new_password) {
                            this.passwordErrorText = error.error.new_password;
                        } else if (error.error.confirm_password) {
                            this.passwordErrorText = error.error.confirm_password;
                        } else if (error.error.non_field_errors) {
                            this.passwordErrorText = error.error.non_field_errors;
                        } else if (error.error.error) {
                            this.passwordErrorText = error.error.error;
                        } else {
                            this.passwordErrorText = 'Failed to update password. Please try again.';
                        }
                    } else {
                        this.passwordErrorText = 'Failed to update password. Please try again.';
                    }
                }
            });
        } else {
            console.log('Form Invalid');
            this.passwordForm.markAllAsTouched();
            this.passwordFormError = true;
            this.passwordErrorText = 'Please fill in all required fields correctly';
        }
    }
    
    // Log out the user
    logOut() {
        this.authService.logOut();
        this.router.navigate(['/login']);
    }
    
    // Toggle password visibility for all fields
    togglePasswordVisibility() {
        this.showPasswords = !this.showPasswords;
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
