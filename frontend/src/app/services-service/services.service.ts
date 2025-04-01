import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth-service/auth.service';
import { environment } from '../../../env/environment';

@Injectable({
  providedIn: 'root'
})
export class ServicesService {
private apiUrl = `${environment.apiHost}/api/services`;

  constructor(private http: HttpClient) { }

  getServices(token: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}`, { headers });
  }

  getServicesByCategories(token: string, id:any): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/?category=${id}`, { headers });
  }

  getServiceCategories(token: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${environment.apiHost}/api/categories`, { headers });
  }

  createService(token: string, servData: any): Observable<any> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    return this.http.post(`${this.apiUrl}/`, servData, { headers });
  }
}
