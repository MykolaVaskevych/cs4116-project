import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { FormsModule } from '@angular/forms';


@Component({
  selector: 'app-update-booking',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Update Booking Status</h2>
    <div>
      <label>Booking ID:</label>
      <input [(ngModel)]="bookingId" placeholder="Booking ID">
    </div>
    <div>
      <label>New Status:</label>
      <select [(ngModel)]="newStatus">
        <option value="confirmed">Confirmed</option>
        <option value="completed">Completed</option>
        <option value="cancelled">Cancelled</option>
      </select>
    </div>
    <button (click)="onUpdate()">Update Status</button>
    <p>{{responseMessage}}</p>
  `
})
export class UpdateBookingComponent {
  bookingId = '';
  newStatus = 'confirmed';
  responseMessage = '';
  private baseUrl = 'http://127.0.0.1:8000/api/bookings/';

  constructor(private http: HttpClient) {}

  onUpdate() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Login as provider or moderator.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const url = `${this.baseUrl}${this.bookingId}/update-status/`;
    const payload = { status: this.newStatus };
    this.http.patch(url, payload, { headers }).subscribe({
      next: (res: any) => {
        this.responseMessage = res.detail || 'Booking updated.';
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to update booking.';
      }
    });
  }
}
