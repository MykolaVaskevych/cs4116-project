import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AuthService } from './auth-service/auth.service';
import { Observable } from 'rxjs';
import { environment } from '../env/environment';

@Injectable({
  providedIn: 'root'
})
export class UserProfileService {
  private apiUrl = `${environment.apiHost}/api/profile`;

  constructor(private http: HttpClient, private authService: AuthService) { }

  getProfile(token: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}`, { headers });
  }

  updateProfile(token: string, profileData: any): Observable<any> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json'); // Ensure JSON request format
    return this.http.patch(`${this.apiUrl}/`, profileData, { headers });
  }

  updatePassword(token: string, data: any) {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json'); // Ensure JSON request format
    return this.http.post(`${environment.apiHost}/api/change-password/`, data, { headers });
  }
  
  updateProfileImage(token: string, formData: FormData) {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`);
    // Note: Don't set Content-Type for FormData, browser will set it automatically with boundary
    return this.http.patch(`${this.apiUrl}/`, formData, { headers });
  }
}
