import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})
export class ProfileComponent implements OnInit {
  userData: any = {};
  backendUrl = 'http://127.0.0.1:8000/api/profile/';
  responseMessage = '';
  oldPassword = '';
  newPassword = '';
  passwordChangeMessage = '';
  constructor(private http: HttpClient, private router: Router) {}

  ngOnInit() {
    // On page load, fetch user info
    const token = localStorage.getItem('access_token');
    if (!token) {
      // TODO: redirect to login page not working here, line 41 does
      this.router.navigate(['/login']);
      return;
    }

    // pass token in the header
    const headers = new HttpHeaders({ 
      Authorization: `Bearer ${token}`
    });

    this.http.get(this.backendUrl, { headers }).subscribe({
      next: (res) => {
        this.userData = res;
      },
      error: (err) => {
        console.error('Profile load error:', err);
        this.responseMessage = 'Failed to load profile.';
        this.router.navigate(['/login']);
      }
    });
  }

  onSave() {
    // for editing user info, do PUT or PATCH
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }
    const headers = new HttpHeaders({ 
      Authorization: `Bearer ${token}`
    });
    
    this.http.put(this.backendUrl, this.userData, { headers }).subscribe({
      next: (res) => {
        this.responseMessage = 'Profile updated successfully!';
      },
      error: (err) => {
        console.error('Profile update error:', err);
        this.responseMessage = 'Failed to update profile.';
      }
    });
  }

  onChangePassword() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.router.navigate(['/login']);
      return;
    }
    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  
    const payload = {
      old_password: this.oldPassword,
      new_password: this.newPassword
    };
  
    this.http.post('http://127.0.0.1:8000/api/change-password/', payload, { headers }).subscribe({
      next: (res: any) => {
        this.passwordChangeMessage = res.detail || 'Password changed.';
      },
      error: (err) => {
        this.passwordChangeMessage = err.error?.detail || 'Error changing password.';
      }
    });
  }
  
}
