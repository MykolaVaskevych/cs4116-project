import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth-service/auth.service';

@Injectable({
  providedIn: 'root'
})
export class ReviewsService {
private apiUrl = 'http://localhost:8000/api/services';

  constructor(private http: HttpClient) { }

  getReviews(token: string, id: any): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/${id}/reviews`, { headers });
  }
}
