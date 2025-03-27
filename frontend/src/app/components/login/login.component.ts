import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {AuthService} from '../../services/auth-service/auth.service';
import {NgForOf, NgIf} from '@angular/common';

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

    constructor(private router: Router, private authService: AuthService) {
        this.loginForm = new FormGroup({
            email: new FormControl(''),
            password: new FormControl(''),
        });
    }

    logInButton(event: Event): void {
        event.preventDefault();
        this.errorListAfterSignUp = [];

        this.authService.login({
            email: this.loginForm.value.email,
            password: this.loginForm.value.password
        }).subscribe(result => {
            console.log(result);
            localStorage.setItem('access', result.access);
            localStorage.setItem('refresh', result.refresh);
            localStorage.setItem('user', JSON.stringify(result.user));

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
