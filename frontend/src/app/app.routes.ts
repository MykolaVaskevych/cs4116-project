import { Routes } from '@angular/router';
import {HomeComponent} from './components/home/home.component';
import {AboutComponent} from './components/about/about.component';
import {LoginComponent} from './components/login/login.component';
import {SignUpComponent} from './components/sign-up/sign-up.component';
import {AuthGuard} from './services/auth-guard/authGuard';
import {InquiryComponent} from './components/inquiry/inquiry.component';
import {RequestPaymentComponent} from './components/request-payment/request-payment.component';
import {
    PaymentRequestCustomerViewComponent
} from './components/payment-request-customer-view/payment-request-customer-view.component';

export let routes: Routes;
routes = [
    {path: 'home', component: HomeComponent, canActivate: [AuthGuard]},
    {path: 'about', component: AboutComponent, canActivate: [AuthGuard]},
    {path: 'login', component: LoginComponent, canActivate: [AuthGuard]},
    {path: 'sign-up', component: SignUpComponent, canActivate: [AuthGuard]},
    {path: 'inquiry', component: InquiryComponent, canActivate: [AuthGuard]},
    {path: 'modal', component: PaymentRequestCustomerViewComponent, canActivate: [AuthGuard]},
    {path: '', redirectTo: '/home', pathMatch: 'full'},
];
