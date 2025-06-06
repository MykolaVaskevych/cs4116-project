import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AboutComponent } from './components/about/about.component';
import { LoginComponent } from './components/login/login.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { AuthGuard } from './services/auth-guard/authGuard';
import { ProfileComponent } from './components/profile/profile.component';
import { ServiceListingComponent } from './components/service-listing/service-listing.component';
import { ListingDetailsComponent } from './components/listing-details/listing-details.component';
import { CreateListingComponent } from './components/create-listing/create-listing.component';
import { CreateBlogComponent } from './components/create-blog/create-blog.component';
import { BlogsComponent } from './components/blogs/blogs.component';
import { BlogDetailComponent } from './components/blog-detail/blog-detail.component';
import { InquiryComponent } from './components/inquiry/inquiry.component';
import { PaymentRequestCustomerViewComponent } from './components/payment-request-customer-view/payment-request-customer-view.component';
import { CustomerToCustomerComponent } from './components/customer-to-customer/customer-to-customer.component';
import { SupportListComponent } from './components/support-list/support-list.component';
import { SupportChatComponent } from './components/support-chat/support-chat.component';
import { RequestPaymentComponent } from './components/request-payment/request-payment.component';

export let routes: Routes;
routes = [
    { path: 'home', component: HomeComponent, canActivate: [AuthGuard] },
    { path: 'about', component: AboutComponent, canActivate: [AuthGuard] },
    { path: 'p2p', component: CustomerToCustomerComponent, canActivate: [AuthGuard] },
    { path: 'login', component: LoginComponent, canActivate: [AuthGuard] },
    { path: 'sign-up', component: SignUpComponent, canActivate: [AuthGuard] },
    { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
    { path: 'service-listing', component: ServiceListingComponent, canActivate: [AuthGuard] },
    { path: 'inquiry', component: InquiryComponent, canActivate: [AuthGuard] },
    { path: 'inquiry/:id', component: InquiryComponent, canActivate: [AuthGuard] },
    { path: 'listing-details', component: ListingDetailsComponent, canActivate: [AuthGuard] },
    { path: 'create-listing', component: CreateListingComponent, canActivate: [AuthGuard] },
    { path: 'create-blog', component: CreateBlogComponent, canActivate: [AuthGuard] },
    { path: 'blogs', component: BlogsComponent, canActivate: [AuthGuard] },
    { path: 'blogs/:slug', component: BlogDetailComponent, canActivate: [AuthGuard] },
    { path: 'modal', component: PaymentRequestCustomerViewComponent, canActivate: [AuthGuard] },
    { path: 'payment-requests', component: PaymentRequestCustomerViewComponent, canActivate: [AuthGuard] },
    { path: 'request-payment', component: RequestPaymentComponent, canActivate: [AuthGuard] },
    { path: 'support', component: SupportListComponent, canActivate: [AuthGuard] },
    { path: 'support/:id', component: SupportChatComponent, canActivate: [AuthGuard] },
    { path: '', redirectTo: '/home', pathMatch: 'full' },
];
