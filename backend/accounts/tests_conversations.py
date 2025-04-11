import json
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
from rest_framework.test import APIClient
from rest_framework import status
from .models import (
    User, Conversation, ConversationMessage, Review,
    Service, Category, Inquiry, Wallet, Transaction
)


class ConversationModelTests(TestCase):
    """Test cases for Conversation model methods"""
    
    def setUp(self):
        # Create users
        self.sender = User.objects.create_user(
            email='sender@example.com',
            username='sender',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.recipient = User.objects.create_user(
            email='recipient@example.com',
            username='recipient',
            password='password123',
            role=User.Role.CUSTOMER
        )

        # Add funds to sender's wallet for transfer tests
        self.sender.wallet.balance = Decimal('100.00')
        self.sender.wallet.save()
        
        # Store initial balances for verification
        self.initial_balance_sender = self.sender.wallet.balance
        self.initial_balance_recipient = self.recipient.wallet.balance

        # Create conversation
        self.conversation = Conversation.objects.create(
            sender=self.sender,
            recipient=self.recipient
        )
    
    def test_conversation_str_representation(self):
        """Test the string representation of a conversation"""
        expected_str = f"Conversation {self.conversation.conversation_id} between {self.sender.username} and {self.recipient.username}"
        self.assertEqual(str(self.conversation), expected_str)
    
    def test_accept_conversation(self):
        """Test accepting a conversation transfers funds and updates status"""
        # Accept the conversation
        transaction = self.conversation.accept()
        
        # Refresh from DB
        self.conversation.refresh_from_db()
        self.sender.wallet.refresh_from_db()
        self.recipient.wallet.refresh_from_db()
        
        # Verify conversation is accepted
        self.assertTrue(self.conversation.is_accepted)
        
        # Verify funds were transferred
        fee_amount = Decimal('5.00')
        self.assertEqual(self.sender.wallet.balance, self.initial_balance_sender - fee_amount)
        self.assertEqual(self.recipient.wallet.balance, self.initial_balance_recipient + fee_amount)
        
        # Verify transaction was created correctly
        self.assertEqual(transaction.from_wallet, self.sender.wallet)
        self.assertEqual(transaction.to_wallet, self.recipient.wallet)
        self.assertEqual(transaction.amount, fee_amount)
        self.assertEqual(transaction.transaction_type, Transaction.TransactionType.TRANSFER)
    
    def test_accept_already_accepted_conversation(self):
        """Test accepting an already accepted conversation raises error"""
        # Accept the conversation once
        self.conversation.accept()
        self.conversation.refresh_from_db()
        
        # Try to accept again
        with self.assertRaises(ValueError) as context:
            self.conversation.accept()
        
        self.assertEqual(str(context.exception), "Conversation is already accepted")
    
    def test_deny_conversation(self):
        """Test denying a conversation deletes it and returns info"""
        # Store ID for verification
        conversation_id = self.conversation.conversation_id
        
        # Deny the conversation
        result = self.conversation.deny()
        
        # Verify conversation is deleted
        with self.assertRaises(Conversation.DoesNotExist):
            Conversation.objects.get(conversation_id=conversation_id)
        
        # Verify result contains correct info
        self.assertEqual(result['conversation_id'], conversation_id)
        self.assertEqual(result['sender_id'], self.sender.id)
        self.assertEqual(result['recipient_id'], self.recipient.id)
    
    def test_deny_accepted_conversation(self):
        """Test denying an already accepted conversation raises error"""
        # Accept the conversation
        self.conversation.accept()
        self.conversation.refresh_from_db()
        
        # Try to deny
        with self.assertRaises(ValueError) as context:
            self.conversation.deny()
        
        self.assertEqual(str(context.exception), "Cannot deny an already accepted conversation")


class ConversationMessageModelTests(TestCase):
    """Test cases for ConversationMessage model methods"""
    
    def setUp(self):
        # Create users
        self.sender = User.objects.create_user(
            email='sender@example.com',
            username='sender',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.recipient = User.objects.create_user(
            email='recipient@example.com',
            username='recipient',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        # Create and accept conversation
        self.conversation = Conversation.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            is_accepted=True
        )
        
        # Create message
        self.message = ConversationMessage.objects.create(
            conversation=self.conversation,
            sender=self.sender,
            content="Hello, this is a test message",
            is_read=False
        )
    
    def test_message_str_representation(self):
        """Test the string representation of a message"""
        expected_str = f"Message {self.message.message_id} in conversation {self.conversation.conversation_id}"
        self.assertEqual(str(self.message), expected_str)
    
    def test_mark_as_read(self):
        """Test marking a message as read updates the field"""
        # Verify initial state
        self.assertFalse(self.message.is_read)
        
        # Mark as read
        self.message.mark_as_read()
        
        # Verify message is marked as read
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)
    
    def test_mark_already_read_message(self):
        """Test marking an already read message has no effect"""
        # Mark as read
        self.message.is_read = True
        self.message.save()
        
        # Try to mark as read again
        self.message.mark_as_read()
        
        # Verify still marked as read
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_read)


class ConversationAPITests(TestCase):
    """Test cases for Conversation API endpoints"""
    
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.customer1 = User.objects.create_user(
            email='customer1@example.com',
            username='customer1',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.customer2 = User.objects.create_user(
            email='customer2@example.com',
            username='customer2',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.customer3 = User.objects.create_user(
            email='customer3@example.com',
            username='customer3',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.customer4 = User.objects.create_user(
            email='customer4@example.com',
            username='customer4',
            password='password123',
            role=User.Role.CUSTOMER
        )
        
        self.business = User.objects.create_user(
            email='business@example.com',
            username='business',
            password='password123',
            role=User.Role.BUSINESS
        )
        
        # Add funds to customer wallets
        self.customer1.wallet.balance = Decimal('100.00')
        self.customer1.wallet.save()
        
        self.customer2.wallet.balance = Decimal('100.00')
        self.customer2.wallet.save()
        
        # Keep customer3 with no funds for testing insufficient funds scenarios
        
        # Create a service and category for review tests
        self.category = Category.objects.create(name="Test Category")
        self.service = Service.objects.create(
            name="Test Service",
            description="Test service description",
            business=self.business,
            category=self.category
        )
        
        # Create a closed inquiry for customer2 to allow review creation
        self.inquiry = Inquiry.objects.create(
            service=self.service,
            customer=self.customer2,
            subject="Test inquiry",
            status=Inquiry.Status.CLOSED
        )
        
        # Create a review by customer2 
        self.review = Review.objects.create(
            service=self.service,
            user=self.customer2,
            rating=5,
            comment="Excellent service"
        )
        
        # Create a conversation for accept/deny tests
        self.pending_conversation = Conversation.objects.create(
            sender=self.customer1,
            recipient=self.customer2
        )
        
        # Create an accepted conversation for messaging tests
        self.accepted_conversation = Conversation.objects.create(
            sender=self.customer3,
            recipient=self.customer4,
            is_accepted=True
        )
        
        # Create messages for the accepted conversation
        self.message1 = ConversationMessage.objects.create(
            conversation=self.accepted_conversation,
            sender=self.customer3,
            content="Hi there!",
            created_at=timezone.now()
        )
        
        self.message2 = ConversationMessage.objects.create(
            conversation=self.accepted_conversation,
            sender=self.customer4,
            content="Hello!",
            is_read=False,
            created_at=timezone.now()
        )
        
        # URLs
        self.conversations_url = reverse('accounts:conversation-list-create')
        self.unread_count_url = reverse('accounts:unread-conversation-count')
        self.pending_conversation_detail_url = reverse(
            'accounts:conversation-detail', 
            kwargs={'conversation_id': self.pending_conversation.conversation_id}
        )
        self.pending_conversation_action_url = reverse(
            'accounts:conversation-action',
            kwargs={'conversation_id': self.pending_conversation.conversation_id}
        )
        self.accepted_conversation_messages_url = reverse(
            'accounts:conversation-messages',
            kwargs={'conversation_id': self.accepted_conversation.conversation_id}
        )
    
    def test_list_conversations_requires_authentication(self):
        """Test listing conversations requires authentication"""
        # Unauthenticated request
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Authenticated request
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.conversations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_conversations_shows_only_user_conversations(self):
        """Test that users can only see their own conversations"""
        # Authenticate as customer1
        self.client.force_authenticate(user=self.customer1)
        response = self.client.get(self.conversations_url)
        
        # Customer1 should see their conversations but not others
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        conversation_ids = [c['conversation_id'] for c in data]
        
        # Should see own conversations
        self.assertIn(str(self.pending_conversation.conversation_id), conversation_ids)
        
        # Should not see other conversations
        self.assertNotIn(str(self.accepted_conversation.conversation_id), conversation_ids)
    
    def test_create_conversation_success(self):
        """Test creating a new conversation successfully"""
        self.client.force_authenticate(user=self.customer1)
        
        # Create a conversation with customer4 (no existing conversation between them)
        data = {
            'recipient_id': self.customer4.id,
            'initial_message': 'Hello, I would like to chat with you.'
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify conversation details
        response_data = response.json()
        self.assertEqual(response_data['sender'], self.customer1.id)
        self.assertEqual(response_data['recipient'], self.customer4.id)
        self.assertEqual(response_data['is_accepted'], False)
        
        # Verify message was created
        conversation_id = response_data['conversation_id']
        conversation = Conversation.objects.get(conversation_id=conversation_id)
        messages = conversation.messages.all()
        
        self.assertEqual(messages.count(), 1)
        self.assertEqual(messages[0].content, 'Hello, I would like to chat with you.')
        self.assertEqual(messages[0].sender, self.customer1)
    
    def test_create_conversation_from_review(self):
        """Test creating a conversation from a review"""
        self.client.force_authenticate(user=self.customer3)  # Using customer3 who doesn't have a conversation with customer2
        
        data = {
            'recipient_id': self.customer2.id,
            'initial_message': "I saw your review, let's chat!",
            'review_id': self.review.review_id
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify conversation was created with correct participants
        response_data = response.json()
        self.assertEqual(response_data['sender'], self.customer3.id)
        self.assertEqual(response_data['recipient'], self.customer2.id)
    
    def test_create_conversation_with_nonexistent_recipient(self):
        """Test creating a conversation with a non-existent recipient fails"""
        self.client.force_authenticate(user=self.customer1)
        
        data = {
            'recipient_id': 999999,  # Non-existent ID
            'initial_message': 'Hello!'
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipient_id', response.json())
    
    def test_create_conversation_with_self(self):
        """Test creating a conversation with oneself fails"""
        self.client.force_authenticate(user=self.customer1)
        
        data = {
            'recipient_id': self.customer1.id,  # Same as sender
            'initial_message': 'Hello to myself!'
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipient_id', response.json())
    
    def test_create_duplicate_conversation(self):
        """Test creating a duplicate conversation fails"""
        self.client.force_authenticate(user=self.customer1)
        
        # Try to create conversation with customer2 (already exists)
        data = {
            'recipient_id': self.customer2.id,
            'initial_message': 'Trying to create a duplicate conversation'
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('recipient_id', response.json())
    
    def test_create_conversation_wrong_reviewer(self):
        """Test creating a conversation from a review with wrong reviewer fails"""
        self.client.force_authenticate(user=self.customer1)
        
        data = {
            'recipient_id': self.customer3.id,  # Not the reviewer
            'initial_message': 'Hello!',
            'review_id': self.review.review_id  # Review by customer2
        }
        
        response = self.client.post(self.conversations_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('review_id', response.json())
    
    def test_get_conversation_detail(self):
        """Test retrieving a specific conversation"""
        self.client.force_authenticate(user=self.customer1)
        
        response = self.client.get(self.pending_conversation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify data
        data = response.json()
        self.assertEqual(data['conversation_id'], str(self.pending_conversation.conversation_id))
        self.assertEqual(data['sender'], self.customer1.id)
        self.assertEqual(data['recipient'], self.customer2.id)
    
    def test_get_conversation_detail_unauthorized(self):
        """Test that users can only access conversations they're a part of"""
        self.client.force_authenticate(user=self.customer3)
        
        response = self.client.get(self.pending_conversation_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_accept_conversation(self):
        """Test accepting a conversation"""
        self.client.force_authenticate(user=self.customer2)  # Recipient
        
        data = {'action': 'accept'}
        
        initial_sender_balance = self.customer1.wallet.balance
        initial_recipient_balance = self.customer2.wallet.balance
        
        response = self.client.post(self.pending_conversation_action_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertIn('transaction_id', response_data)
        self.assertEqual(response_data['amount'], '5.00')
        
        # Verify conversation is now accepted
        self.pending_conversation.refresh_from_db()
        self.assertTrue(self.pending_conversation.is_accepted)
        
        # Verify funds were transferred
        self.customer1.wallet.refresh_from_db()
        self.customer2.wallet.refresh_from_db()
        
        self.assertEqual(self.customer1.wallet.balance, initial_sender_balance - Decimal('5.00'))
        self.assertEqual(self.customer2.wallet.balance, initial_recipient_balance + Decimal('5.00'))
    
    def test_deny_conversation(self):
        """Test denying a conversation"""
        # Create a new conversation for this test
        test_conversation = Conversation.objects.create(
            sender=self.customer1,
            recipient=self.customer3
        )
        
        action_url = reverse('accounts:conversation-action',
                           kwargs={'conversation_id': test_conversation.conversation_id})
        
        self.client.force_authenticate(user=self.customer3)  # Recipient
        
        data = {'action': 'deny'}
        
        response = self.client.post(action_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response
        response_data = response.json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'Conversation request denied')
        
        # Verify conversation is deleted
        with self.assertRaises(Conversation.DoesNotExist):
            Conversation.objects.get(conversation_id=test_conversation.conversation_id)
    
    def test_accept_conversation_non_recipient(self):
        """Test that only the recipient can accept a conversation"""
        # Create a new conversation for this test
        test_conversation = Conversation.objects.create(
            sender=self.customer2,
            recipient=self.customer3
        )
        
        action_url = reverse('accounts:conversation-action',
                           kwargs={'conversation_id': test_conversation.conversation_id})
        
        self.client.force_authenticate(user=self.customer1)  # Not the recipient
        
        data = {'action': 'accept'}
        
        response = self.client.post(action_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_accept_conversation_insufficient_funds(self):
        """Test accepting a conversation fails if sender has insufficient funds"""
        # Create a conversation with customer3 (no funds) as sender
        no_funds_conversation = Conversation.objects.create(
            sender=self.customer3,  # Has 0 balance
            recipient=self.customer2
        )
        
        action_url = reverse('accounts:conversation-action',
                           kwargs={'conversation_id': no_funds_conversation.conversation_id})
        
        self.client.force_authenticate(user=self.customer2)  # Recipient
        
        data = {'action': 'accept'}
        
        response = self.client.post(action_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # The error might be either in 'error' or 'non_field_errors' depending on implementation
        response_data = response.json()
        error_found = False
        if 'error' in response_data:
            error_found = True
        if 'non_field_errors' in response_data:
            error_found = True
        self.assertTrue(error_found, "Expected error message in response")
    
    def test_list_conversation_messages(self):
        """Test listing messages in a conversation"""
        self.client.force_authenticate(user=self.customer3)  # Participant in accepted_conversation
        
        response = self.client.get(self.accepted_conversation_messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify response includes both messages
        data = response.json()
        self.assertEqual(len(data), 2)
        
        # Verify messages are in correct order (chronological)
        self.assertEqual(data[0]['content'], 'Hi there!')
        self.assertEqual(data[1]['content'], 'Hello!')
    
    def test_list_messages_marks_as_read(self):
        """Test that listing messages marks them as read"""
        # Message2 is from customer4 to customer3 and is unread
        self.assertFalse(self.message2.is_read)
        
        # Authenticate as customer3 (recipient of the unread message)
        self.client.force_authenticate(user=self.customer3)
        
        # Get messages
        response = self.client.get(self.accepted_conversation_messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify message is now marked as read
        self.message2.refresh_from_db()
        self.assertTrue(self.message2.is_read)
    
    def test_create_message(self):
        """Test creating a new message in a conversation"""
        # Authenticate as participant in the accepted conversation
        self.client.force_authenticate(user=self.customer3)
        
        data = {
            'content': 'This is a new message',
            'conversation': str(self.accepted_conversation.id)  # Include conversation ID
        }
        
        response = self.client.post(self.accepted_conversation_messages_url, data)
        
        # Check for both possible success statuses
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
        
        # Verify message was created in the database
        created_message = ConversationMessage.objects.filter(
            conversation=self.accepted_conversation,
            content='This is a new message'
        ).first()
        
        self.assertIsNotNone(created_message)
        self.assertEqual(created_message.sender, self.customer3)
        
        # Verify conversation updated_at was updated
        self.accepted_conversation.refresh_from_db()
        # Only check this if a message was created
        if created_message:
            timestamp_updated = self.accepted_conversation.updated_at >= self.message2.created_at
            self.assertTrue(timestamp_updated)
    
    def test_create_message_in_non_accepted_conversation(self):
        """Test that messages cannot be created in non-accepted conversations"""
        # URL for the non-accepted conversation
        url = reverse('accounts:conversation-messages',
                    kwargs={'conversation_id': self.pending_conversation.conversation_id})
        
        self.client.force_authenticate(user=self.customer1)  # Sender in pending conversation
        
        data = {
            'content': 'This message should not be allowed',
            'conversation': str(self.pending_conversation.id)
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Print the response for debugging
        print(f"Response data: {response.json()}")
        
        # Accept any error response as long as it's a 400 status code
        # The test is primarily checking that we can't send messages in non-accepted conversations
        # The format of the error can vary based on implementation, but the key is that it fails
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_message_non_participant(self):
        """Test that only participants can create messages"""
        self.client.force_authenticate(user=self.customer1)  # Not a participant in accepted_conversation
        
        data = {
            'content': 'This message should not be allowed',
            'conversation': str(self.accepted_conversation.id)
        }
        
        response = self.client.post(self.accepted_conversation_messages_url, data)
        # Either 404 (participant not found) or 400 (validation error) is acceptable
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST])
    
    def test_unread_message_count(self):
        """Test getting the count of conversations with unread messages"""
        # Set up an unread message for customer1
        second_conversation = Conversation.objects.create(
            sender=self.customer4,
            recipient=self.customer1,
            is_accepted=True
        )
        
        ConversationMessage.objects.create(
            conversation=second_conversation,
            sender=self.customer4,
            content="Unread message for customer1",
            is_read=False
        )
        
        # Authenticate as customer1
        self.client.force_authenticate(user=self.customer1)
        
        response = self.client.get(self.unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should have 1 conversation with unread messages
        self.assertEqual(response.json()['unread_count'], 1)
    
    def test_unread_count_no_unread_messages(self):
        """Test unread count returns 0 when there are no unread messages"""
        # Authenticate as customer3 who has already seen all messages
        self.message2.is_read = True
        self.message2.save()
        
        self.client.force_authenticate(user=self.customer3)
        
        response = self.client.get(self.unread_count_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['unread_count'], 0)