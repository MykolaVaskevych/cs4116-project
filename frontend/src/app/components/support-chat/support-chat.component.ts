import { Component, OnInit, OnDestroy } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { SupportService } from '../../services/support-service/support.service';
import { AuthService } from '../../services/auth-service/auth.service';
import { interval, Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { User } from '../../models/user.model';

@Component({
  selector: 'app-support-chat',
  templateUrl: './support-chat.component.html',
  styleUrls: ['./support-chat.component.css'],
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})
export class SupportChatComponent implements OnInit, OnDestroy {
  ticket: any;
  messages: any[] = [];
  messageForm: FormGroup;
  ticketId: string | null = null;
  loading = false;
  error: string | null = null;
  currentUser: User | null = null;
  isModerator = false;
  pollingSubscription: Subscription | null = null;

  constructor(
    private supportService: SupportService,
    private authService: AuthService,
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder
  ) {
    this.messageForm = this.fb.group({
      content: ['', [Validators.required]]
    });
  }

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.isModerator = this.currentUser?.role === 'MODERATOR';
    
    console.log('Current user:', this.currentUser);
    console.log('Is moderator:', this.isModerator);
    
    this.route.paramMap.subscribe(params => {
      const id = params.get('id');
      if (id) {
        console.log('Support chat received ticket ID:', id);
        this.ticketId = id;
        this.loadTicket();
        this.loadMessages();
        this.startPolling();
      } else {
        this.error = 'Ticket ID is missing';
      }
    });
  }

  ngOnDestroy(): void {
    if (this.pollingSubscription) {
      this.pollingSubscription.unsubscribe();
    }
  }

  startPolling(): void {
    this.pollingSubscription = interval(5000).subscribe(() => {
      if (this.ticketId) {
        this.loadMessages(false);
        // Also refresh ticket details occasionally
        this.loadTicket(false);
      }
    });
  }

  loadTicket(showLoading = true): void {
    if (!this.ticketId) return;
    
    console.log('Loading ticket details for ID:', this.ticketId);
    
    if (showLoading) {
      this.loading = true;
    }
    
    this.supportService.getSupportConversation(this.ticketId).subscribe({
      next: (data) => {
        console.log('Ticket data received:', data);
        this.ticket = data;
        if (showLoading) {
          this.loading = false;
        }
      },
      error: (err) => {
        this.error = `Error loading support ticket: ${err.status} ${err.statusText}`;
        if (showLoading) {
          this.loading = false;
        }
        console.error('Ticket loading error:', err);
        console.error(`Failed URL: ${this.supportService.getApiUrl()}/support/tickets/${this.ticketId}/`);
      }
    });
  }

  loadMessages(showLoading = true): void {
    if (!this.ticketId) return;
    
    console.log('Loading messages for ticket ID:', this.ticketId);
    
    if (showLoading) {
      this.loading = true;
    }
    
    this.supportService.getSupportMessages(this.ticketId).subscribe({
      next: (data) => {
        console.log('Messages received:', data);
        this.messages = data;
        if (showLoading) {
          this.loading = false;
        }
        this.scrollToBottom();
      },
      error: (err) => {
        this.error = `Error loading messages: ${err.status} ${err.statusText}`;
        if (showLoading) {
          this.loading = false;
        }
        console.error('Message loading error:', err);
        console.error(`Failed URL: ${this.supportService.getApiUrl()}/support/tickets/${this.ticketId}/messages/`);
      }
    });
  }

  sendMessage(): void {
    if (this.messageForm.invalid || !this.ticketId) return;
    
    console.log('Sending message to ticket:', this.ticketId);
    
    const message = {
      content: this.messageForm.value.content
    };
    
    console.log('Message payload:', message);
    
    this.loading = true;
    this.supportService.sendSupportMessage(this.ticketId, message).subscribe({
      next: (response) => {
        console.log('Message sent successfully:', response);
        this.messageForm.reset();
        this.loadMessages();
      },
      error: (err) => {
        this.error = 'Failed to send message: ' + (err.error?.detail || err.message || JSON.stringify(err.error) || 'Unknown error');
        this.loading = false;
        console.error('Error sending message:', err);
        console.error('Error details:', err.error);
      }
    });
  }

  isCurrentUserMessage(message: any): boolean {
    // Check both user_id and user fields to handle different API response formats
    if (this.currentUser == null) return false;
    
    if (message.user && message.user.id) {
      return message.user.id === this.currentUser.id;
    } else if (message.user_id) {
      return message.user_id === this.currentUser.id;
    }
    
    return false;
  }
  
  isModeratorMessage(message: any): boolean {
    // For system messages (like ticket closed notifications)
    if (message.is_system_message === true) {
      return true;
    }
    
    // For the new support ticket system, check for is_from_moderator flag
    if (message.is_from_moderator === true) {
      return true;
    }
    
    // Fallback to checking user role
    if (message.user && message.user.role === 'MODERATOR') {
      return true;
    }
    
    return false;
  }
  
  isSystemMessage(message: any): boolean {
    return message.is_system_message === true;
  }

  scrollToBottom(): void {
    setTimeout(() => {
      const messageContainer = document.querySelector('.messages-container');
      if (messageContainer) {
        messageContainer.scrollTop = messageContainer.scrollHeight;
      }
    }, 100);
  }
  
  goBack(): void {
    this.router.navigate(['/support']);
  }
  
  closeTicket(): void {
    if (!this.ticketId || !this.isModerator) return;
    
    console.log('Closing ticket:', this.ticketId);
    this.loading = true;
    
    this.supportService.closeSupportConversation(this.ticketId).subscribe({
      next: (response) => {
        console.log('Ticket closed successfully:', response);
        // Update the ticket data
        this.ticket = response;
        this.loading = false;
        
        // Add a system message
        this.messages.push({
          content: 'This ticket has been closed by the moderator. No further messages can be sent.',
          created_at: new Date(),
          is_from_moderator: true,
          sender_name: 'System',
          is_system_message: true
        });
        
        this.scrollToBottom();
      },
      error: (err) => {
        this.error = 'Failed to close ticket: ' + (err.error?.detail || err.message || 'Unknown error');
        this.loading = false;
        console.error('Error closing ticket:', err);
      }
    });
  }
}