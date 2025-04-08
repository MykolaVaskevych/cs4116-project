import { Component } from '@angular/core';
import {Router} from '@angular/router';
import { AuthService } from '../../services/auth-service/auth.service';
import Swal from 'sweetalert2';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {NgForOf, NgIf} from '@angular/common';

@Component({
  selector: 'app-sign-up',
    imports: [
        ReactiveFormsModule,
        NgIf,
        NgForOf
    ],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.css'
})
export class SignUpComponent {
    signUpForm: FormGroup;
    invalidItems = '';
    errorListAfterSignUp = [];

    constructor(private router: Router, private authService: AuthService) {
        this.signUpForm = new FormGroup({
            email: new FormControl('', [Validators.required, Validators.email]),
            username: new FormControl('', [Validators.required]),
            password: new FormControl('', [Validators.required]),
            repeatPassword: new FormControl('', [Validators.required]),
        },
            { validators: passwordMatchValidator() }
        );
    }

    signUpButton(event: Event): void {
        event.preventDefault();

        if (this.signUpForm.valid) {
            console.log(this.signUpForm.value);

            this.authService.register({
                username: this.signUpForm.value.username,
                email: this.signUpForm.value.email,
                password: this.signUpForm.value.password,
            }).subscribe(res => {
                console.log(res);

                Swal.fire({
                    icon: "success",
                    position: "top-end",
                    showConfirmButton: false,
                    timer: 1500,
                    timerProgressBar: true,
                    title: "Success!",
                });

                this.router.navigate(['home']);
            }, error => {
                this.errorListAfterSignUp = [];
                Object.values(error.error).forEach(message => {
                    // @ts-ignore
                    this.errorListAfterSignUp.push(message[0]);
                })
            });


        } else {
            this.invalidItems = '';
            Object.keys(this.signUpForm.controls).forEach(controlName => {
                const control = this.signUpForm.get(controlName);
                if (control && control.invalid) {
                    if (this.invalidItems.length > 0) {
                        this.invalidItems += ', ';
                    }
                    this.invalidItems += controlName;
                    console.log(`${controlName} is invalid`);
                    console.log('Errors:', control.errors);  // Log the validation errors for each invalid control
                    console.log(this.invalidItems)
                }
            });
        }
    }
}

import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

// Custom validator to check if password and repeatPassword match
export function passwordMatchValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
        const password = control.get('password')?.value;
        const repeatPassword = control.get('repeatPassword')?.value;

        // Check if both fields are present and match
        if (password && repeatPassword && password !== repeatPassword) {
            return { passwordsNotMatching: true };  // Error key can be anything meaningful
        }

        return null;  // No error if passwords match or are empty
    };
}

