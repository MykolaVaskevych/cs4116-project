import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-moderate-service',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Approve or Reject a Service</h2>
    <div>
      <label>Service ID:</label>
      <input [(ngModel)]="serviceId" placeholder="Service ID">
    </div>
    <button (click)="onApprove()">Approve Service</button>
    <button (click)="onReject()">Reject Service</button>
    <p>{{responseMessage}}</p>
  `
})
export class ModerateServiceComponent {
  serviceId = '';
  responseMessage = '';

  constructor(private http: HttpClient) {}

  onApprove() {
    this.moderate('approve');
  }

  onReject() {
    this.moderate('reject');
  }

  private moderate(action: 'approve'|'reject') {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please login as moderator.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const url = `http://127.0.0.1:8000/api/services/${this.serviceId}/${action}/`;
    this.http.post(url, {}, { headers }).subscribe({
      next: (res: any) => {
        this.responseMessage = res.detail || `Service ${action}ed.`;
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || `Failed to ${action} service.`;
      }
    });
  }
}
