import { Injectable } from '@angular/core';
import {environment} from '../../../env/environment';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {AuthService} from '../auth-service/auth.service';
import {CommonUtilsService} from '../common-utils/common-utils.service';
import {Observable} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConversationService {
    private apiUrl = `${environment.apiHost}/api/conversations`;

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

    createConversationFromReview(payload: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/`, payload, { headers });
    }

    getConversation(conversation_id: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/${conversation_id}/`, { headers });
    }

    sendMessage(conversation_id: any, message: any): Observable<any> {
        const headers = this.getHeadersWithJwt();
        return this.http.post(`${this.apiUrl}/${conversation_id}/messages/`, message, { headers });
    }

    acceptOrDeny(conversation_id: any, action: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.post(`${this.apiUrl}/${conversation_id}/respond/`, { action }, { headers });
    }

    listConversation(): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/`, { headers });
    }

    listMessages(conversation_id: any): Observable<any> {
        const headers = this.getHeadersWithJwt();

        return this.http.get(`${this.apiUrl}/${conversation_id}/messages/`, { headers });
    }

}
