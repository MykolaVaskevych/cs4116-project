import {CanActivateFn, Router} from '@angular/router';
import {AuthService} from '../auth-service/auth.service';
import {inject} from '@angular/core';
import {jwtDecode} from 'jwt-decode';
import {CommonUtilsService} from '../common-utils/common-utils.service';

export const AuthGuard: CanActivateFn = (route, state) => {
    const commonUtilsService = inject(CommonUtilsService);
    const authService = inject(AuthService);
    const router = inject(Router);

    //  NEW CODE JWT EXPIRATION CHECK: START
    let token = authService.getJWT();

    if (token) {
        try {
            const decodedToken = jwtDecode(token);
            const currentTime = Math.floor(Date.now() / 1000);

            if(decodedToken.exp && decodedToken.exp < currentTime) {
                authService.logOut();
                router.navigate(['/login']);

                commonUtilsService.showSessionExpired();
                return false;
            }
        } catch (error) {
            authService.logOut();
            router.navigate(['/login']);

            commonUtilsService.showSessionExpired();
            return false;
        }

        if (route.routeConfig?.path === 'login' || route.routeConfig?.path === 'sign-up') {
            router.navigate(['/home']);
            return false;
        }
        return true;
    } else {
        // @ts-ignore
        if (route.routeConfig?.path === 'login' || route.routeConfig?.path === 'sign-up') {
            return true;
        }
        router.navigate(['/login']);
        return false;
    }
    //  NEW CODE JWT EXPIRATION CHECK: END

    // PREVIOUS CODE: START
    // if (authService.isLoggedIn()) {
    //     if (route.routeConfig?.path === 'login' || route.routeConfig?.path === 'sign-up') {
    //         router.navigate(['/home']);
    //         return false;
    //     }
    //     return true;
    // } else {
    //     // @ts-ignore
    //     if (route.routeConfig?.path === 'login' || route.routeConfig?.path === 'sign-up') {
    //         return true;
    //     }
    //     router.navigate(['/login']);
    //     return false;
    // }
    // PREVIOUS CODE: END
};
