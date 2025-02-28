import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-create-booking',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Create a Booking</h2>
    <form (ngSubmit)="onSubmit()">
      <div>
        <label>Service ID:</label>
        <input [(ngModel)]="serviceId" name="serviceId" required>
      </div>
      <div>
        <label>Schedule Date:</label>
        <input type="datetime-local" [(ngModel)]="scheduleDate" name="scheduleDate" required>
      </div>
      <div>
        <label>Notes:</label>
        <textarea [(ngModel)]="notes" name="notes"></textarea>
      </div>
      <button type="submit">Create Booking</button>
    </form>
    <p>{{ responseMessage }}</p>
  `
})
export class CreateBookingComponent {
  serviceId = '';
  scheduleDate = '';
  notes = '';
  responseMessage = '';
  private endpoint = 'http://127.0.0.1:8000/api/bookings/create/';

  constructor(private http: HttpClient) {}

  onSubmit() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please login first.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const payload = {
      service: this.serviceId,
      schedule_date: this.scheduleDate,
      notes: this.notes
    };
    this.http.post(this.endpoint, payload, { headers }).subscribe({
      next: (res) => {
        this.responseMessage = 'Booking created with status=pending.';
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to create booking.';
      }
    });
  }
}
