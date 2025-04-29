import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../../env/environment';
import { AuthService } from '../auth-service/auth.service';

@Injectable({
  providedIn: 'root'
})
export class SupportService {
  private baseUrl = `${environment.apiHost}/api`;

  constructor(private http: HttpClient, private authService: AuthService) { }
  
  getApiUrl(): string {
    return this.baseUrl;
  }
  
  private getHeaders(): HttpHeaders {
    const token = this.authService.getJWT();
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    });
  }

  // Get all support tickets for the current user
  getSupportConversations(): Observable<any> {
    return this.http.get(`${this.baseUrl}/support/tickets/`, { headers: this.getHeaders() });
  }

  // Get a specific support ticket
  getSupportConversation(id: string | number): Observable<any> {
    return this.http.get(`${this.baseUrl}/support/tickets/${id}/`, { headers: this.getHeaders() });
  }

  // Create a new support ticket
  createSupportConversation(data: any): Observable<any> {
    console.log('Creating support ticket with data:', {
      title: data.title,
      initial_message: data.message
    });
    
    return this.http.post(`${this.baseUrl}/support/tickets/`, {
      title: data.title,
      initial_message: data.message // Match the field name expected by the backend
    }, { headers: this.getHeaders() })
    .pipe(
      catchError(error => {
        console.error('Support ticket creation failed:', error);
        console.error('Request details:', {
          url: `${this.baseUrl}/support/tickets/`,
          payload: {
            title: data.title,
            initial_message: data.message
          },
          headers: this.getHeaders()
        });
        return throwError(() => error);
      })
    );
  }

  // Get messages for a support ticket
  getSupportMessages(ticketId: string | number): Observable<any> {
    return this.http.get(`${this.baseUrl}/support/tickets/${ticketId}/messages/`, { headers: this.getHeaders() });
  }

  // Send a message in a support ticket
  sendSupportMessage(ticketId: string | number, data: any): Observable<any> {
    console.log('Service sending message to ticket:', ticketId);
    console.log('Message payload:', data);
    
    return this.http.post(`${this.baseUrl}/support/tickets/${ticketId}/messages/`, {
      content: data.content
    }, { headers: this.getHeaders() }).pipe(
      catchError(error => {
        console.error('Failed to send message:', error);
        console.error('Request details:', {
          url: `${this.baseUrl}/support/tickets/${ticketId}/messages/`,
          payload: { content: data.content },
          headers: this.getHeaders()
        });
        return throwError(() => error);
      })
    );
  }
  
  // Close a support ticket
  closeSupportConversation(ticketId: string | number): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/support/tickets/${ticketId}/close/`, 
      {}, // No body needed
      { headers: this.getHeaders() }
    );
  }

  // Report a service provider
  reportServiceProvider(serviceId: number, reason: string): Observable<any> {
    return this.http.post(
      `${this.baseUrl}/services/${serviceId}/report/`, 
      { reason },
      { headers: this.getHeaders() }
    );
  }

  // Get unread message count
  getUnreadCount(): Observable<any> {
    return this.http.get(`${this.baseUrl}/support/unread/`, { headers: this.getHeaders() });
  }
}
