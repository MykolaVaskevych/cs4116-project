import { Component } from '@angular/core';
import { AuthService } from '../../services/auth-service/auth.service';

@Component({
  selector: 'app-about',
  imports: [],
  templateUrl: './about.component.html',
  styleUrl: './about.component.css'
})
export class AboutComponent {
  constructor(private authService: AuthService) {}

  contactUs(): void {
    // You can replace this with actual contact form functionality
    alert('Thank you for your interest! Our contact form will be available soon.');
  }
}
