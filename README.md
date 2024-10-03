# Customer & Order Management API

This API is designed to manage customer records and their associated orders. It includes functionality for creating, retrieving, and managing customers and orders. Additionally, it integrates with Google OAuth 2.0 for authentication, and Twilio for sending SMS alerts when a new order is created.

## Requirements

- Python 3.x
- Flask
- SQLAlchemy (or any ORM)
- Google OAuth 2.0 credentials
- AFRICASTAK credentials (for sending SMS)

# API Endpoints
## Customer Routes

1. Create a Customer
Endpoint: /api/customer
Method: POST
Description: Creates a new customer.
Body (JSON):

`````{
    "name": "Customer Name",
    "phone": "Customer Phone Number"
}
````

Response (JSON):

{
    "message": "customer created successfully"
}


2. Retrieve All Customers

Endpoint: /api/customers
Method: GET
Description: Retrieves a list of all customers.
Authentication: Requires Google OAuth login
Response (JSON):

[
    {
        "id": 1,
        "name": "Customer Name",
        "phone": "Customer Phone Number"
    },
    ...
]


## Order Routes
1.Create an Order

Endpoint: /api/order
Method: POST
Description: Creates a new order associated with a customer using the customer’s phone number.
Request Body (JSON)
{
    "phone": "Customer Phone Number",
    "item": "Item Name",
    "amount": "Order Amount"
}

Response (JSON):
{
    "message": "Order created successfully"
}


SMS Notification: An SMS is sent to the customer’s phone number notifying them of the new order.
Status Codes:
201: Order created successfully
400: Bad request (e.g., missing or invalid fields)
404: Customer not found

2.Get Customer's Order Statement

Endpoint: /api/order/<phone>
Method: GET
Description: Retrieves all orders associated with a customer using their phone number.
Response (JSON)

{
    "customer_name": "Customer Name",
    "phone": "Customer Phone Number",
    "orders": [
        {
            "order_id": 1,
            "item": "Item Name",
            "amount": "Order Amount",
            "created_at": "2024-10-01 12:00:00"
        },
        ...
    ]
}


Retrieve All Orders

Endpoint: /api/orders
Method: GET
Description: Retrieves a list of all orders along with associated customer details.
Response (JSON

[
    {
        "item": "Item Name",
        "amount": "Order Amount",
        "time": "Order Creation Time",
        "customer": "Customer Name",
        "phone": "Customer Phone Number"
    },
    ...
]


# Google OAuth Authentication
Google Login

Endpoint: /google/login
Method: GET
Description: Redirects the user to Google's OAuth 2.0 authorization server for authentication.
Google Authentication Callback

Endpoint: /google/auth/

Method: POST

Description: Callback endpoint for handling the response from Google's OAuth 2.0 server.

Action: Stores the OAuth credentials in the session and redirects the user to the customer retrieval endpoint (/api/customers).

Note: The API requires authentication via Google OAuth to retrieve customers and orders.
