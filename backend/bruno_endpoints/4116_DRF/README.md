# Bruno API Collection

This collection contains API endpoint definitions for testing the backend services using [Bruno](https://www.usebruno.com/).

## Getting Started

1. Install Bruno from [https://www.usebruno.com/downloads](https://www.usebruno.com/downloads)
2. Open Bruno and import this collection
3. Set up the environment variables in Bruno:
   - `host`: Base URL of the API server (e.g., `http://127.0.0.1:8000`)
   - `token`: JWT token obtained after login

## Available Endpoints

### Authentication
- Register
- Login

### Profile
- Get Profile
- Update Profile

### Services
- List Services
- Get Service Details
- Create Service (Business only)
- Update Service (Business only)
- Delete Service (Business only)
- Get My Services (Business only)

### Inquiries
- List Inquiries
- Create Inquiry (Customer)
- Get Inquiry Details
- Close Inquiry (Moderator only)

### Messages
- List Messages
- Send Message

### Moderators (New)
- List Moderators
- Request Moderator

### Payment Requests (New)
- List Payment Requests
- List Pending Requests
- Create Payment Request (Business only)
- Get Payment Request
- Respond to Payment Request (Accept/Decline)

### Wallet & Transactions
- Get Wallet
- Deposit to Wallet
- Withdraw from Wallet
- Transfer to Another User
- List Transactions

### Reviews
- List Service Reviews
- Create Service Review
- Get Review Details
- Update Review
- Delete Review
- List Review Comments
- Create Review Comment
- Update Review Comment
- Delete Review Comment

### Blog
- List Blog Categories
- Create Blog Category
- List Blog Posts
- Create Blog Post
- Get Blog Post by Slug
- Create Blog Comment
- List User Blog Posts

## Authentication

Most endpoints require authentication via JWT token. After logging in, set the `token` variable in your environment to the access token received from the login response. This token will be automatically included in the Authorization header for all authenticated requests.

## Testing Flow

When testing payment requests, follow this general flow:

1. Log in as a business user
2. Create a payment request for an existing inquiry
3. Log in as the customer user
4. List pending payment requests
5. Accept or decline the payment request
6. Check wallet balance to verify funds transferred (if accepted)

For moderator requests, follow this flow:

1. Log in as a customer or business user
2. Create an inquiry (if needed)
3. Request a moderator for the inquiry
4. Verify the inquiry now has a moderator assigned