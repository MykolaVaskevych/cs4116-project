import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-request-business',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2>Request Business Account</h2>
    <p>{{responseMessage}}</p>
    <button (click)="onRequest()">Request</button>
  `
})
export class RequestBusinessComponent {
  responseMessage = '';
  private endpoint = 'http://127.0.0.1:8000/api/request-business/';

  constructor(private http: HttpClient) {}

  onRequest() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please login first.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    this.http.post(this.endpoint, {}, { headers }).subscribe({
      next: (res: any) => {
        this.responseMessage = res.detail || 'Request sent.';
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to request business account.';
      }
    });
  }
}
