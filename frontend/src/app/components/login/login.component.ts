import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {AuthService} from '../../services/auth-service/auth.service';
import {NgForOf, NgIf} from '@angular/common';
import { UserProfileService } from '../../services/user-profile.service';

@Component({
  selector: 'app-login',
    imports: [
        ReactiveFormsModule,
        NgForOf,
        NgIf
    ],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
    loginForm: FormGroup;
    errorListAfterSignUp = [];
    token: any
    user: any

    constructor(private router: Router, private authService: AuthService, private userProfileService: UserProfileService) {
        this.loginForm = new FormGroup({
            email: new FormControl(''),
            password: new FormControl(''),
        });
    }

    loadUserProfile() {
        this.userProfileService.getProfile(this.token).subscribe({
            next: (response) => {
                this.user = response;
                console.log('user', this.user)

                if(this.user.role === 'BUSINESS')
                    localStorage.setItem('isProvider', JSON.stringify(true));
                else
                    localStorage.setItem('isProvider', JSON.stringify(false));

                    console.log('isProvider', JSON.parse(localStorage.getItem('isProvider') || 'false'));

            },
          error: (error) => {
            console.error('Error fetching profile', error);
          }
        });
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
            localStorage.setItem('user', JSON.stringify(result.user));
            this.token =  localStorage.getItem('access');
            this.loadUserProfile()

            this.router.navigate(['home']);
        }, error => {
            console.log(error);

            Object.values(error.error).forEach(message => {
                // @ts-ignore
                this.errorListAfterSignUp.push(message);
            })
        });
    }
}
