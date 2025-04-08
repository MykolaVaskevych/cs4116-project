import { Component } from '@angular/core';
import { FormGroup, FormBuilder } from '@angular/forms';
import { BlogService } from '../../services/blog.service';
import { CommonModule } from '@angular/common';
import { UserProfileService } from '../../services/user-profile.service';

@Component({
  selector: 'app-blogs',
  imports: [CommonModule],
  templateUrl: './blogs.component.html',
  styleUrl: './blogs.component.css'
})
export class BlogsComponent {
    token: any;
    categories: any;
    blogs: any
    user: any
    selectedBlog: any

    constructor(
        private blogService: BlogService, private fb: FormBuilder, private userProfileService: UserProfileService
    ) { }

     ngOnInit() {
            this.token = localStorage.getItem('access');
            console.log('token', this.token);

            this.getBlogPosts()
            this.getBlogCategories();
            this.loadUserProfile()
        }

    getBlogCategories() {
        this.blogService.getBlogCategories(this.token).subscribe({
            next: (response) => {
                this.categories = response;
                console.log('categories', this.categories);

            },
            error: (error) => {
                console.error('Error fetching categories', error);
            }
        });
    }

    getBlogPosts() {
        this.blogService.getBlogPosts(this.token).subscribe({
            next: (response) => {
                this.blogs = response;
                console.log('blogs', this.blogs);

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    getBlogPostsByCat(id: any) {
        this.blogService.getPostsByCategory(this.token, id).subscribe({
            next: (response) => {
                this.blogs = response;
                console.log('blogs', this.blogs);

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    getBlogPostsBySlug(slug: any) {
        this.blogService.getPostBySlug(this.token, slug).subscribe({
            next: (response) => {
                this.selectedBlog = response;
                console.log('blog by slug', this.selectedBlog);

            },
            error: (error) => {
                console.error('Error fetching blogs', error);
            }
        });
    }

    loadUserProfile() {


        this.userProfileService.getProfile(this.token).subscribe({
          next: (response) => {
            this.user = response;
            console.log('user', this.user)
          },
          error: (error) => {
            console.error('Error fetching profile', error);
          }
        });

      }


}
