import { Component } from '@angular/core';
import {AuthService} from '../../services/auth-service/auth.service';
import {NgbTooltip} from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-topbar',
    imports: [
        NgbTooltip
    ],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.css'
})
export class TopbarComponent {
    constructor(private authService: AuthService) {
    }

    logOut(): void {
        this.authService.logOut();
    }
}
