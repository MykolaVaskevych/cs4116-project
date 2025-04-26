import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../auth-service/auth.service';
import { environment } from '../../../env/environment';

export interface Service {
  id: number;
  name: string;
  description: string;
  logo: string;
  category: number;
  category_name: string;
  fixed_price: number;
  created_at: string;
  updated_at: string;
  business: number;
  business_name: string;
  rating?: number;
}

export interface Category {
  id: number;
  name: string;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class ServicesService {
  private apiUrl = `${environment.apiHost}/api/services`;

  constructor(private http: HttpClient) { }

  /**
   * Get all services with optional filters
   */
  getServices(
    token: string, 
    search?: string,
    category?: number,
    price_min?: number,
    price_max?: number
  ): Observable<Service[]> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    let params = new HttpParams();
    
    // Add optional filters
    if (search) {
      params = params.set('search', search);
    }
    
    if (category) {
      params = params.set('category', category.toString());
    }
    
    if (price_min !== undefined) {
      params = params.set('price_min', price_min.toString());
    }
    
    if (price_max !== undefined) {
      params = params.set('price_max', price_max.toString());
    }
    
    return this.http.get<Service[]>(`${this.apiUrl}`, { 
      headers,
      params
    });
  }

  /**
   * Get services by category ID
   */
  getServicesByCategories(token: string, id: any): Observable<Service[]> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get<Service[]>(`${this.apiUrl}/?category=${id}`, { headers });
  }

  /**
   * Get service categories
   */
  getServiceCategories(token: string): Observable<Category[]> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get<Category[]>(`${environment.apiHost}/api/categories`, { headers });
  }

  /**
   * Create a service (without image)
   */
  createService(token: string, servData: any): Observable<Service> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    return this.http.post<Service>(`${this.apiUrl}/`, servData, { headers });
  }
  
  /**
   * Create a service with image upload
   */
  createServiceWithImage(token: string, formData: FormData): Observable<Service> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`);
    // Don't set Content-Type here, it will be set automatically with boundary for FormData
    
    return this.http.post<Service>(`${this.apiUrl}/`, formData, { headers });
  }
  
  /**
   * Get service details by ID
   */
  getServiceDetails(token: string, id: number): Observable<Service> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get<Service>(`${this.apiUrl}/${id}/`, { headers });
  }
}
