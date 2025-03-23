# API Changes and New Features

This document details the recent API changes and new features added to the backend. Frontend developers should use this guide to understand how to integrate with the new endpoints.

## Table of Contents

1. [Payment Request Management](#payment-request-management)
   - [Overview](#payment-request-overview)
   - [Endpoints](#payment-request-endpoints)
   - [Data Models](#payment-request-data-models)
   - [Example Requests and Responses](#payment-request-examples)

2. [Moderator Management](#moderator-management)
   - [Overview](#moderator-management-overview)
   - [Endpoints](#moderator-management-endpoints)
   - [Data Models](#moderator-management-data-models)
   - [Example Requests and Responses](#moderator-management-examples)

3. [Changes to Existing APIs](#changes-to-existing-apis)
   - [Inquiry Creation](#inquiry-creation-changes)

---

## Payment Request Management

### Payment Request Overview

The payment request system allows business users to create targeted payment requests directed at specific customers within an existing inquiry. Customers can then either accept the payment request, which automatically triggers a fund transfer, or decline the request.

Key features:
- Business users can create payment requests for customers in active inquiries
- Customers can view pending payment requests directed to them
- Customers can accept or decline payment requests
- Accepted payments are automatically processed through the wallet system
- Payment requests store status information (pending, accepted, or declined)

### Payment Request Endpoints

#### 1. List Payment Requests

**Endpoint:** `GET /api/payment-requests/`

**Description:** Returns a list of payment requests filtered by user role.
- For business users: Returns payment requests they've created
- For customers: Returns payment requests directed to them
- For moderators: Returns all payment requests

**Auth Required:** Yes

**Query Parameters:**
- `status`: Filter by status (PENDING, ACCEPTED, DECLINED)
- `inquiry`: Filter by inquiry ID

**Response Example:**
```json
[
  {
    "id": 1,
    "request_id": "e964c113-1846-46c7-abf8-6962b1635e7f",
    "inquiry": 1,
    "creator": 2,
    "creator_name": "business",
    "recipient": 1,
    "recipient_name": "customer",
    "amount": "100.00",
    "description": "Payment for cleaning services",
    "status": "PENDING",
    "status_display": "Pending",
    "service_name": "Home Cleaning",
    "transaction": null,
    "transaction_id": null,
    "created_at": "2023-03-22T15:30:00Z",
    "updated_at": "2023-03-22T15:30:00Z"
  }
]
```

#### 2. List Pending Payment Requests

**Endpoint:** `GET /api/payment-requests/pending/`

**Description:** Returns all pending payment requests directed to the authenticated user.

**Auth Required:** Yes

**Response:** Same format as the List Payment Requests endpoint, but filtered to only show pending requests for the current user.

#### 3. Create Payment Request

**Endpoint:** `POST /api/payment-requests/`

**Description:** Creates a new payment request for a customer in an existing inquiry.

**Auth Required:** Yes

**Permissions:** Only business users can create payment requests

**Request Body:**
```json
{
  "inquiry": 1,
  "amount": "100.00",
  "description": "Payment for cleaning services"
}
```

**Response:** Returns the created payment request object

#### 4. Get Payment Request Details

**Endpoint:** `GET /api/payment-requests/{request_id}/`

**Description:** Returns details of a specific payment request.

**Auth Required:** Yes

**Permissions:** Users can only view payment requests they created or received

**Response:** Returns the detailed payment request object

#### 5. Respond to Payment Request

**Endpoint:** `POST /api/payment-requests/{request_id}/respond/`

**Description:** Accepts or declines a payment request.

**Auth Required:** Yes

**Permissions:** Only the recipient of the payment request can respond to it

**Request Body:**
```json
{
  "action": "accept" // or "decline"
}
```

**Response for Accept:**
```json
{
  "message": "Payment request accepted",
  "transaction_id": "12345678-1234-5678-1234-567812345678",
  "amount": "100.00",
  "new_balance": "400.00"
}
```

**Response for Decline:**
```json
{
  "message": "Payment request declined"
}
```

### Payment Request Data Models

The payment request system introduces a new model with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| request_id | UUID | Unique identifier for the payment request |
| inquiry | ForeignKey | Reference to the inquiry this payment request is for |
| creator | ForeignKey | The business user who created the request |
| recipient | ForeignKey | The customer who will receive the request |
| amount | Decimal | The amount requested |
| description | Text | Description of what this payment is for |
| status | String | Current status (PENDING, ACCEPTED, DECLINED) |
| transaction | ForeignKey | Reference to transaction record (when accepted) |
| created_at | DateTime | When the request was created |
| updated_at | DateTime | When the request was last updated |

### Payment Request Examples

#### Creating a Payment Request (Business User)

```javascript
// Example JavaScript fetch request
const createPaymentRequest = async () => {
  const response = await fetch('/api/payment-requests/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + accessToken
    },
    body: JSON.stringify({
      inquiry: 1,
      amount: '100.00',
      description: 'Payment for cleaning services'
    })
  });
  
  const data = await response.json();
  return data;
};
```

#### Accepting a Payment Request (Customer)

```javascript
// Example JavaScript fetch request
const acceptPaymentRequest = async (requestId) => {
  const response = await fetch(`/api/payment-requests/${requestId}/respond/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + accessToken
    },
    body: JSON.stringify({
      action: 'accept'
    })
  });
  
  const data = await response.json();
  return data;
};
```

---

## Moderator Management

### Moderator Management Overview

The moderator management system has been updated to improve how moderators are assigned to inquiries. Key changes include:

1. Removal of automatic moderator assignment when an inquiry is created
2. Addition of a dedicated system for requesting moderators
3. Implementation of a smart assignment algorithm that assigns the moderator with the fewest active inquiries
4. New endpoints for listing moderators with their inquiry counts

### Moderator Management Endpoints

#### 1. List Moderators

**Endpoint:** `GET /api/moderators/`

**Description:** Returns a list of all moderators with their active inquiry counts.

**Auth Required:** Yes

**Response Example:**
```json
[
  {
    "id": 3,
    "username": "moderator1",
    "email": "moderator1@example.com",
    "first_name": "Mod",
    "last_name": "One",
    "profile_image": "/media/profile_images/mod1.jpg",
    "active_inquiry_count": 5
  },
  {
    "id": 4,
    "username": "moderator2",
    "email": "moderator2@example.com",
    "first_name": "Mod",
    "last_name": "Two",
    "profile_image": "/media/profile_images/mod2.jpg",
    "active_inquiry_count": 2
  }
]
```

#### 2. Request Moderator

**Endpoint:** `POST /api/moderators/request/`

**Description:** Allows customers and businesses to explicitly request a moderator for an active inquiry.

**Auth Required:** Yes

**Permissions:** Only participants in the inquiry (customer or business) can request a moderator

**Request Body:**
```json
{
  "inquiry_id": 1
}
```

**Response:** Returns the inquiry object with updated moderator information

**Validation:**
- If a moderator is already assigned, the request will be rejected
- If a moderator request has already been made for this inquiry, the request will be rejected
- Only open inquiries can have moderators assigned

### Moderator Management Data Models

The inquiry model has been updated with a new field:

| Field | Type | Description |
|-------|------|-------------|
| has_moderator_request | Boolean | Indicates if a moderator has been requested for this inquiry |

### Moderator Management Examples

#### Requesting a Moderator

```javascript
// Example JavaScript fetch request
const requestModerator = async (inquiryId) => {
  const response = await fetch('/api/moderators/request/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + accessToken
    },
    body: JSON.stringify({
      inquiry_id: inquiryId
    })
  });
  
  const data = await response.json();
  return data;
};
```

#### Getting Moderator List with Workload

```javascript
// Example JavaScript fetch request
const getModerators = async () => {
  const response = await fetch('/api/moderators/', {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + accessToken
    }
  });
  
  const data = await response.json();
  return data;
};
```

---

## Changes to Existing APIs

### Inquiry Creation Changes

The inquiry creation process has been updated to no longer automatically assign a moderator. This change allows customers and businesses to explicitly request moderators when needed.

**What's Changed:**
- When creating an inquiry, no moderator is assigned by default
- Users must explicitly request a moderator using the new moderator request endpoint
- The moderator field in the inquiry response may be null until a moderator is requested

**Important Note for Frontend:**
- Update any UI that assumes all inquiries have moderators
- Add UI elements for requesting moderators as needed
- Consider adding indication when an inquiry has no moderator assigned