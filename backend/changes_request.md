# Project API Changes and Updates

## New APIs

### Payment Request Management

#### Endpoints

- Retrieve Pending Requests: Fetches all payment requests currently awaiting approval for the authenticated user.
- Create Payment Request: Allows business users to create targeted payment requests directed at specific users within an existing inquiry.
- Check Request Status: Enables both the request creator and recipient to verify the current status of payment requests by using a unique request identifier or the related inquiry ID.

#### User Workflow

Users who receive a payment request have two actions available:

- Accept: Automatically triggers a fund transfer from the recipient to the request creator (business).
- Decline: Marks the request as declined without any further processing.

#### Data Management

- Payment requests are temporarily stored with clear status indicators (pending, accepted, or declined) to facilitate timely responses and status verification.
- Upon status resolution:
  - Declined requests are immediately removed from temporary storage.
  - Accepted requests are transferred to permanent transaction records.

### Moderator Management

#### Endpoint

- List All Moderators: Provides a complete list of moderators along with their current count of active inquiries.

#### Moderator Assignment Logic

- Smart Assignment: Automatically assigns the moderator with the fewest active inquiries.

## Updated APIs

### Moderator Assignment Updates

#### Changes to Moderator Assignment Logic

- Automatic assignment of moderators at inquiry creation will be removed.

#### Moderator Request Endpoint

- Introduces a dedicated API allowing customers and businesses to explicitly request moderators for active inquiries.
- Limits each inquiry to only one moderator assignment request:
  - If a moderator is already assigned, additional assignment requests for that inquiry are prohibited.

#### Moderator Participation Requirements

- Moderators are automatically added to inquiries upon receiving an assignment request.
- Moderators cannot decline an assignment request once issued.
