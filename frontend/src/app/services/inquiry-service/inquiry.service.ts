import {Injectable} from '@angular/core';
import {environment} from '../../../env/environment';
import {Observable, switchMap} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {AuthService} from '../auth-service/auth.service';
import {CommonUtilsService} from '../common-utils/common-utils.service';

@Injectable({
  providedIn: 'root'
})
export class InquiryService {
    private randomUsrApi = `${environment.randomUserApi}/api`;
    private apiUrl = `${environment.apiHost}/api`; // Example API URL

    constructor(private http: HttpClient, private authService: AuthService, private commonUtilsService: CommonUtilsService) { }

    getJWT() {
        return this.authService.getJWT();
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


    // Inquiry API:
    getAllInquiries(): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/inquiries/`, { headers });
    }

    getSingleInquiry(inquiry_id: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/inquiries/${inquiry_id}/`, { headers });
    }

    closeInquiry(inquiry_id: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/inquiries/${inquiry_id}/close/`, {}, { headers });
    }

    sendInquiryMessage(content: any, inquiry: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/messages/`, { content, inquiry }, { headers });
    }

    getInquiryMessage(inquiry: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/messages/?inquiry=${inquiry}`, { headers });
    }

    // Payment Request API

    createPaymentRequest(paymentRequest: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/payment-requests/`, paymentRequest, { headers });
    }

    getPaymentRequest(): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/payment-requests/`, { headers });
    }

    getPaymentRequestByUUID(uuid: any): Observable<any> {
        const headers = this.getHeadersWithJwt();
        return this.http.get(`${this.apiUrl}/payment-requests/${uuid}/`, { headers });
    }

    acceptOrDeclinePaymentRequest(uuid: any, action: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/payment-requests/${uuid}/respond/`, { action }, { headers });
    }
}
