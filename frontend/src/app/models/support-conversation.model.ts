/**
 * Interface for Support Conversations
 * Represents support conversations between users and moderators
 */
export interface SupportConversation {
  id: number;
  title: string;
  user: number;
  user_username?: string;
  moderator?: number;
  moderator_username?: string;
  status: 'OPEN' | 'CLOSED';
  created_at: string;
  updated_at: string;
  unread_count?: number;
  customer_unread_count?: number;
  last_message?: {
    id: number;
    content: string;
    sender_name: string;
    timestamp: string;
  };
}

/**
 * Interface for Support Messages
 * Represents messages in a support conversation
 */
export interface SupportMessage {
  id: number;
  conversation: number;
  sender: number;
  sender_name?: string;
  sender_role?: string;
  content: string;
  created_at: string;
  is_read: boolean;
}