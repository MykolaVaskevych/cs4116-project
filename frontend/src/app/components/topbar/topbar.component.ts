import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth-service/auth.service';
import { NgbTooltip } from '@ng-bootstrap/ng-bootstrap';
import { CommonModule } from '@angular/common';
import { CommonUtilsService } from '../../services/common-utils/common-utils.service';

@Component({
  selector: 'app-topbar',
  imports: [
    NgbTooltip,
    CommonModule
  ],
  templateUrl: './topbar.component.html',
  styleUrl: './topbar.component.css'
})
export class TopbarComponent implements OnInit {
  current_user_login: any;
  current_user_role: any;
  isLoggedIn: boolean = false;

  constructor(private authService: AuthService, private commonUtilsService: CommonUtilsService) {
  }

  ngOnInit(): void {
    const current_user = this.commonUtilsService.getCurrentUser();
    if (current_user) {
      this.current_user_login = current_user.username;
      this.current_user_role = current_user.role;
      this.isLoggedIn = true;
    }
  }
  
  logOut(): void {
    this.authService.logOut();
  }
}
