# P2P Chat API Endpoints

This section contains endpoints for the peer-to-peer chat functionality, allowing users to communicate directly with each other.

## Key Features

1. Users can start conversations from reviews
2. Recipients must accept conversation requests before messages can be exchanged
3. When a conversation is accepted, a 5€ fee is transferred from sender to recipient
4. Messages can only be sent in accepted conversations
5. Unread message count tracking for notifications

## Endpoints

1. **List Conversations**  
   `GET /api/conversations/`  
   Lists all conversations the authenticated user is participating in.

2. **Create Conversation**  
   `POST /api/conversations/`  
   Creates a new conversation with initial message.

3. **Create Conversation From Review**  
   `POST /api/conversations/`  
   Creates a new conversation with a reviewer.

4. **Get Conversation Details**  
   `GET /api/conversations/{conversation_id}/`  
   Retrieves details of a specific conversation.

5. **Accept Conversation**  
   `POST /api/conversations/{conversation_id}/respond/`  
   Accepts a conversation request, transferring 5€ from sender to recipient.

6. **Deny Conversation**  
   `POST /api/conversations/{conversation_id}/respond/`  
   Denies and deletes a conversation request.

7. **List Messages**  
   `GET /api/conversations/{conversation_id}/messages/`  
   Retrieves all messages in a conversation, marking unread messages as read.

8. **Send Message**  
   `POST /api/conversations/{conversation_id}/messages/`  
   Sends a new message in a conversation.

9. **Get Unread Count**  
   `GET /api/conversations/unread-count/`  
   Gets the number of conversations with unread messages.

## Workflow

1. User initiates a conversation (optionally from a review)
2. Recipient receives the conversation request
3. Recipient accepts or denies the request
4. If accepted, 5€ is transferred and users can exchange messages
5. If denied, the conversation is deleted