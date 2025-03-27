import {Injectable} from '@angular/core';
import {environment} from '../../../env/environment';
import {Observable} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class InquiryService {
    private randomUsrApi = `${environment.randomUserApi}/api`;
    private apiUrl = `${environment.apiHost}/api`; // Example API URL

    constructor(private http: HttpClient) { }

    getJWT() {
        return localStorage.getItem('access');
    }

    getHeadersWithJwt() {
        const access = this.getJWT();

        return new HttpHeaders({
            'Authorization': `Bearer ${access}`
        });
    }

    fetchProfilePicture(numberOfProfiles: number): Observable<any> {
        return this.http.get(`${this.randomUsrApi}/?results=${numberOfProfiles}`);
    }

    getAllInquiries(): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/inquiries/`, { headers });
    }

    sendInquiryMessage(content: any, inquiry: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/messages/`, { content, inquiry }, { headers });
    }

    getInquiryMessage(inquiry: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/messages/?inquiry=${inquiry}`, { headers });
    }
}
