import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { SupportService } from '../../services/support-service/support.service';
import { AuthService } from '../../services/auth-service/auth.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-support-list',
  templateUrl: './support-list.component.html',
  styleUrls: ['./support-list.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class SupportListComponent implements OnInit {
  conversations: any[] = [];
  newConversationForm: FormGroup;
  showNewConversationForm = false;
  loading = false;
  error: string | null = null;
  currentUser: any;
  isModerator = false;

  constructor(
    private supportService: SupportService,
    private authService: AuthService,
    private router: Router,
    private fb: FormBuilder
  ) {
    this.newConversationForm = this.fb.group({
      title: ['', [Validators.required, Validators.maxLength(100)]],
      message: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.isModerator = this.currentUser?.role === 'MODERATOR';
    this.loadConversations();
  }

  loadConversations(): void {
    this.loading = true;
    this.supportService.getSupportConversations().subscribe({
      next: (data) => {
        this.conversations = data;
        console.log('Loaded support tickets:', this.conversations);
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Error loading support tickets';
        this.loading = false;
        console.error(err);
      }
    });
  }

  openConversation(id: string): void {
    console.log('Opening support ticket with ID:', id);
    this.router.navigate(['/support', id]);
  }

  toggleNewConversationForm(): void {
    this.showNewConversationForm = !this.showNewConversationForm;
    if (!this.showNewConversationForm) {
      this.newConversationForm.reset();
    }
  }

  createNewConversation(): void {
    if (this.newConversationForm.invalid) return;
    
    this.loading = true;
    const data = {
      title: this.newConversationForm.value.title,
      message: this.newConversationForm.value.message
    };
    
    this.supportService.createSupportConversation(data).subscribe({
      next: (response) => {
        console.log('Support ticket created successfully:', response);
        // Extract ticket ID from response
        const ticketId = response.id || response.ticket_id;
        if (ticketId) {
          this.router.navigate(['/support', ticketId]);
        } else {
          this.error = 'Invalid ticket ID in response';
          this.loading = false;
          console.error('Invalid response format:', response);
        }
      },
      error: (err) => {
        this.error = 'Failed to create support ticket: ' + (err.error?.detail || err.message || 'Unknown error');
        this.loading = false;
        console.error('Support ticket creation error:', err);
      }
    });
  }

  getLastMessage(ticket: any): string {
    if (ticket.last_message) {
      return ticket.last_message.content.length > 50 
        ? ticket.last_message.content.substring(0, 50) + '...' 
        : ticket.last_message.content;
    }
    return 'No messages';
  }

  getLastMessageTime(ticket: any): string {
    return ticket.last_message ? ticket.last_message.created_at : ticket.created_at;
  }

  hasUnreadMessages(ticket: any): boolean {
    if (this.isModerator) {
      // For moderators, check unread_count (messages from customer to moderator)
      return ticket.unread_count > 0;
    } else {
      // For customers, check moderator_messages_unread count
      return ticket.moderator_messages_unread > 0;
    }
  }
  
  getUnreadCount(ticket: any): number {
    if (this.isModerator) {
      return ticket.unread_count || 0;
    } else {
      return ticket.moderator_messages_unread || 0;
    }
  }
}