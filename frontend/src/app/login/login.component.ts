import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = '';
  password = '';
  responseMessage = '';

  backendUrl = 'http://127.0.0.1:8000/api/login/';

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit() {
    const payload = {
      email: this.email,
      password: this.password,
    };

    this.http.post(this.backendUrl, payload).subscribe({
      next: (res: any) => {
        console.log('Login success:', res);
        // If using JWT, store tokens or user info:
        localStorage.setItem('access_token', res.access);
        localStorage.setItem('refresh_token', res.refresh);

        localStorage.setItem('user_role', res.role);
        localStorage.setItem('user_name', res.username);
        
        // Redirect to home:
        this.router.navigate(['/']);
      },
      error: (err) => {
        console.error('Login error:', err);
        // If there's a detailed error, show it. Otherwise a fallback message.
        const details = err.error?.detail || 'Login failed.';
        this.responseMessage = `Error: ${details}`;
      }
    });
  }
}
