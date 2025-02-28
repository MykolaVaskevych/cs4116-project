import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { ProfileComponent } from './profile/profile.component';
import { NotFoundComponent } from './not-found/not-found.component';
import { RequestBusinessComponent } from './request-business/request-business.component';
import { ApproveProviderComponent } from './approve-provider/approve-provider.component';
import { CreateServiceComponent } from './create-service/create-service.component';
import { ModerateServiceComponent } from './moderate-service/moderate-service.component';
import { CreateBookingComponent } from './create-booking/create-booking.component';
import { UpdateBookingComponent } from './update-booking/update-booking.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'login', component: LoginComponent },
  { path: 'profile', component: ProfileComponent },
  { path: 'request-business', component: RequestBusinessComponent },
  { path: 'approve-provider', component: ApproveProviderComponent },
  { path: 'create-service', component: CreateServiceComponent },
  { path: 'moderate-service', component: ModerateServiceComponent },
  { path: 'create-booking', component: CreateBookingComponent },
  { path: 'update-booking', component: UpdateBookingComponent },

  // 404
  { path: '**', component: NotFoundComponent },
];
