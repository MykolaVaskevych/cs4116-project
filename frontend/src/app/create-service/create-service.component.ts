import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-create-service',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <h2>Create Service</h2>
    <form (ngSubmit)="onSubmit()">
      <div>
        <label>Title:</label>
        <input [(ngModel)]="title" name="title" required>
      </div>
      <div>
        <label>Description:</label>
        <textarea [(ngModel)]="description" name="description"></textarea>
      </div>
      <div>
        <label>Price:</label>
        <input type="number" [(ngModel)]="price" name="price" required>
      </div>
      <div>
        <label>Category ID:</label>
        <input [(ngModel)]="category" name="category" required>
      </div>
      <button type="submit">Create</button>
    </form>
    <p>{{ responseMessage }}</p>
  `
})
export class CreateServiceComponent {
  title = '';
  description = '';
  price: number | null = null;
  category = '';
  responseMessage = '';
  private endpoint = 'http://127.0.0.1:8000/api/services/create/';

  constructor(private http: HttpClient) {}

  onSubmit() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please login first.';
      return;
    }
    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });
    const payload = {
      title: this.title,
      description: this.description,
      price: this.price,
      category: this.category
    };

    this.http.post(this.endpoint, payload, { headers }).subscribe({
      next: (res) => {
        this.responseMessage = 'Service created (pending approval).';
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to create service.';
      }
    });
  }
}
