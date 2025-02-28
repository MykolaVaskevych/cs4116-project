import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router'

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  passwordConfirm = '';
  responseMessage = '';

  // your Django endpoint
  backendUrl = 'http://127.0.0.1:8000/api/register/';

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit() {
    const payload = {
      username: this.username,
      email: this.email,
      password: this.password,
      password_confirm: this.passwordConfirm,
      first_name: '',
      last_name: '',
      role: 'customer'
    };

    this.http.post(this.backendUrl, payload).subscribe({
      next: (res) => {
        console.log('Registration success:', res);
        this.responseMessage = 'Registration successful!';

        // maybe store tokens? if you want them right away
        // localStorage.setItem('access_token', res.access);
        // localStorage.setItem('refresh_token', res.refresh);

        // redirect to home
        this.router.navigate(['/']);
      },
      error: (err) => {
        console.error('Registration error:', err);
        let msg = 'Registration failed.';
      
        // If err.error is an object with field-based errors:
        if (err.error) {
          // Attempt to build a message from each field
          // For example, { "email": ["Enter a valid email."], "password": ["Too short"] }
          const errorObj = err.error;
          const messages: string[] = [];
      
          for (const key of Object.keys(errorObj)) {
            // Could be an array of errors or a single string
            const val = errorObj[key];
            if (Array.isArray(val)) {
              // e.g. "email": ["Enter a valid email address."]
              messages.push(`${key}: ${val.join(' ')}`);
            } else if (typeof val === 'string') {
              messages.push(`${key}: ${val}`);
            }
          }
          if (messages.length > 0) {
            msg = messages.join(' | ');
          }
        }
      
        this.responseMessage = `Error: ${msg}`;
      }
      
    });
  }
}
