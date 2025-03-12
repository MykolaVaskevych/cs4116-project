import { Component } from '@angular/core';
import {Router, RouterLink, RouterLinkActive, RouterOutlet} from '@angular/router';
import {BusinessListComponent} from './components/business-list/business-list.component';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIf} from '@angular/common';
import {TopbarComponent} from './components/topbar/topbar.component';

@Component({
  selector: 'app-root',
    imports: [RouterOutlet, BusinessListComponent, RouterLink, RouterLinkActive, ReactiveFormsModule, NgIf, TopbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
    constructor(private router: Router) {}

    title = 'marketplace';

    inputControl = new FormControl('');

    // This will hold the value of the input field
    logInputValue() {
        console.log(this.inputControl.value);  // Log the current value of input
    }

    isLoginPage(): boolean {
        return this.router.url === '/login' || this.router.url === '/sign-up';
    }
}
