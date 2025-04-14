import { Injectable } from '@angular/core';
import {jwtDecode} from 'jwt-decode';
import Swal from 'sweetalert2';

@Injectable({
  providedIn: 'root'
})
export class CommonUtilsService {

    constructor() { }

    getCurrentUser() {
        return JSON.parse(<string>localStorage.getItem('user'));
    }

    // Method to check if JWT token is expired
    isTokenExpired(token: any): boolean {
        if (!token) return true;

        try {
            const decoded: any = jwtDecode(token);
            const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds
            return decoded.exp < currentTime;
        } catch (e) {
            return true; // In case decoding fails or token is malformed
        }
    }

    showSessionExpired() {
        return Swal.fire({
            icon: "warning",
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            title: "Session Expired. You've been logged out.",
        });
    }

    showCustomAlert(warning: any, title: any) {
        return Swal.fire({
            icon: warning,
            position: "top-end",
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            title,
        });
    }
}
