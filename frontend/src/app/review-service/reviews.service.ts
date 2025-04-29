import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth-service/auth.service';
import { environment } from '../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class ReviewsService {
  private apiUrl = `${environment.apiHost}/api/services`;
  private reviewsUrl = `${environment.apiHost}/api/reviews`;

  constructor(private http: HttpClient) { }

  getReviews(token: string, id: any): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/${id}/reviews`, { headers });
  }
  
  createReview(token: string, serviceId: any, rating: number, comment: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const body = {
      rating: rating,
      comment: comment
    };
    return this.http.post(`${this.apiUrl}/${serviceId}/reviews/create/`, body, { headers });
  }
  
  updateReview(token: string, reviewId: any, rating: number, comment: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    const body = {
      rating: rating,
      comment: comment
    };
    return this.http.patch(`${this.reviewsUrl}/${reviewId}/`, body, { headers });
  }
  
  deleteReview(token: string, reviewId: any): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.delete(`${this.reviewsUrl}/${reviewId}/`, { headers });
  }
}
