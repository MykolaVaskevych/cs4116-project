import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { jwtDecode } from 'jwt-decode';
import { environment } from '../../../env/environment';
import { User } from '../../models/user.model';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = `${environment.apiHost}/api`;
    accessTokenKey = 'access';
    refreshTokenKey = 'refresh';
    constructor(private http: HttpClient) { }

    register(user: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/register/`, user);
    }

    login(user: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/login/`, user);
    }

    isLoggedIn(): boolean {
        return !!localStorage.getItem('access');    //  'access' is retrieved from the /login URL after successful login.
    }

    logOut(): void {
        localStorage.removeItem('access');
        localStorage.removeItem('isProvider');
        localStorage.removeItem('user');
    }
    // Refresh JWT token: NOW IN ACTION
    refreshJWT(): Observable<any> {
        const refresh = localStorage.getItem(this.refreshTokenKey);
        return this.http.post(`${this.apiUrl}/token/refresh/`, { refresh });
    }

    getJWT(): any {
        return localStorage.getItem(this.accessTokenKey);
    }
    
    // Change password functionality
    changePassword(token: string, passwordData: any): Observable<any> {
        return this.http.post(`${this.apiUrl}/change-password/`, passwordData, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
    }

    getCurrentUser(): User | null {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            return JSON.parse(userStr) as User;
        }
        return null;
    }
    
    getUserProfile(): Observable<any> {
        const token = this.getJWT();
        const headers = new HttpHeaders().set('Authorization', `Bearer ${token}`);
        return this.http.get(`${this.apiUrl}/profile/`, { headers });
    }
}
