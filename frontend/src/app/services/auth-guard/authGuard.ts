import {CanActivateFn, Router} from '@angular/router';
import {AuthService} from '../auth-service/auth.service';
import {inject} from '@angular/core';

export const AuthGuard: CanActivateFn = (route, state) => {
    const authService = inject(AuthService);
    const router = inject(Router);

    if (authService.isLoggedIn()) {
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
};
