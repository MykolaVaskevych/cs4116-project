import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
    private apiUrl = 'http://localhost:8000/api'; // Example API URL

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
    }

}
