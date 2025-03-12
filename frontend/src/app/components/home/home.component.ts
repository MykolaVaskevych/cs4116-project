import { Component } from '@angular/core';
import {NgForOf, NgOptimizedImage, NgStyle} from '@angular/common';

@Component({
  selector: 'app-home',
    imports: [
        NgForOf,
        NgStyle,
    ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
    aboutUsItems = [
        { id: 1, size: '600px', value: '' },
        { id: 2, size: '600px', value: '' },  // Wider
        { id: 3, size: '600px', value: '' },
    ];


    serviceList = [
        { id: 1, title: 'Legal' },
        { id: 2, title: 'Finance' },
        { id: 3, title: 'Lifestyle' },
        { id: 4, title: 'Other' },
    ];
}
