import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-pending-providers',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2>Pending Providers</h2>
    <p *ngIf="responseMessage">{{ responseMessage }}</p>
    <table *ngIf="pendingList.length > 0" border="1">
      <tr>
        <th>User ID</th>
        <th>Username</th>
        <th>Email</th>
        <th>Action</th>
      </tr>
      <tr *ngFor="let user of pendingList">
        <td>{{ user.id }}</td>
        <td>{{ user.username }}</td>
        <td>{{ user.email }}</td>
        <td>
          <button (click)="approveUser(user.id)">Approve</button>
        </td>
      </tr>
    </table>
    <p *ngIf="pendingList.length === 0">No pending providers found.</p>
  `
})
export class PendingProvidersComponent implements OnInit {
  pendingList: any[] = [];
  responseMessage = '';
  private listUrl = 'http://127.0.0.1:8000/api/pending-providers/';
  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.fetchPending();
  }

  fetchPending() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please log in as moderator.';
      return;
    }
    const headers = { headers: new HttpHeaders({ Authorization: `Bearer ${token}` })};
    this.http.get<any[]>(this.listUrl, headers).subscribe({
      next: (res) => {
        this.pendingList = res; // an array of user objects
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to fetch pending providers.';
      }
    });
  }

  approveUser(userId: number) {
    const token = localStorage.getItem('access_token');
    if (!token) {
      this.responseMessage = 'Please log in.';
      return;
    }
    const headers = { headers: new HttpHeaders({ Authorization: `Bearer ${token}` }) };
    const url = `http://127.0.0.1:8000/api/approve-provider/${userId}/`;

    this.http.post(url, {}, headers).subscribe({
      next: (res: any) => {
        this.responseMessage = res.detail || 'Approved.';
        // Remove them from the list
        this.pendingList = this.pendingList.filter(u => u.id !== userId);
      },
      error: (err) => {
        this.responseMessage = err.error?.detail || 'Failed to approve user.';
      }
    });
  }
}
