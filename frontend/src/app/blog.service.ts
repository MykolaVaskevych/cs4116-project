import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from './auth-service/auth.service';
import { environment } from '../env/environment';

@Injectable({
  providedIn: 'root'
})
export class BlogService {
  private apiUrl = `${environment.apiHost}/api/blog`;

  constructor(private http: HttpClient) { }

  getBlogCategories(token: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/categories`, { headers });
  }

  getBlogPosts(token: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/posts`, { headers });
  }

  getPostsByCategory(token: string, categoryId: number): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/posts?category=${categoryId}`, { headers });
  }

  getPostBySlug(token: string, slug: string): Observable<any> {
    const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
    return this.http.get(`${this.apiUrl}/posts/slug/${slug}`, { headers });
  }

  createBlogPost(token: string, blogData: any): Observable<any> {
    const headers = new HttpHeaders()
      .set('Authorization', `Bearer ${token}`)
      .set('Content-Type', 'application/json');

    return this.http.post(`${this.apiUrl}/posts/`, blogData, { headers });
  }

}
