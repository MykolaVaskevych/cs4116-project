import { Component } from '@angular/core';
import { CommonUtilsService } from '../../services/common-utils/common-utils.service';
import { jwtDecode } from 'jwt-decode';
import { AuthService } from '../../services/auth-service/auth.service';
@Component({
  selector: 'app-about',
  imports: [],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  constructor(private authService: AuthService) {
  }
  clickMeButton(): void {
    alert('You Clicked Me !!');

    let accessToken = this.authService.getJWT();
    console.log(accessToken);

    let decode = jwtDecode(accessToken);
    console.log(decode);


    // @ts-ignore
    console.log(Date.now() > decode.exp);
  }
}
