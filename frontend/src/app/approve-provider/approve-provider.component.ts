import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
@Component({
  selector: 'app-approve-provider',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Approve Pending Provider</h2>
    <p>Enter user ID to approve</p>
    <input [(ngModel)]="targetUserId" placeholder="User ID">
    <button (click)="onApprove()">Approve</button>
    <p>{{responseMessage}}</p>
  `
})
export class ApproveProviderComponent {
  targetUserId = '';
  responseMessage = '';

  constructor(private http: HttpClient) {}

  onApprove() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      // this.responseMessage = 'You must be logged in as moderator.';
      this.responseMessage = 'You must be a moderator.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const url = `http://127.0.0.1:8000/api/approve-provider/${this.targetUserId}/`;
    this.http.post(url, {}, { headers }).subscribe({
      next: (res: any) => {
        this.responseMessage = res.detail || 'Provider approved.';
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to approve provider.';
      }
    });
  }
}
