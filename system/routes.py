'''
customer route (crud operation)
'''
import os
import random
import string
from flask import request, jsonify, url_for, redirect, session
from flask_login import login_required, current_user, login_user
from system.model import Customer, Order, User
from system import app, db, oauth, login_manager
from system.sms import SendSMS
from system.validate_phone import is_valid_phone_number
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import google.oauth2.id_token


GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# create customer
@app.route('/api/customer', methods=['POST', 'OPTIONS'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(
        name=data['name'],
        phone=data['phone']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "customer created successfully"}), 201

# Retrieve users
@app.route('/api/customers', methods=['GET'])
def get_customers():
    # Check if the user has credentials in the session
    if 'credentials' not in session:
        return redirect(url_for('google_login'))

    # Verify the user's identity with the credentials in the session
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    request = requests.Request()
    
    try:
        # Verify the ID token to ensure the user is authenticated
        id_info = google.oauth2.id_token.verify_oauth2_token(credentials.id_token, request, GOOGLE_CLIENT_ID)

        # Get user email or other identifying info
        user_email = id_info['email']


        # Fetch customers from the database if the user is authenticated and authorized
        customers = Customer.query.all()
        results = [{"id": c.id, 'name': c.name, 'phone': c.phone} for c in customers]
        return jsonify(results), 200

    except ValueError:
        # If token verification fails, log the user out and redirect to login
        session.clear()
        return redirect(url_for('google_login'))


# create order
@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.get_json()

    # Check if 'phone', 'item', and 'amount' are in the request data
    if 'phone' not in data or 'item' not in data or 'amount' not in data:
        return jsonify({'error': 'Phone number, item, and amount are required'}), 400

    phone = data['phone']
    item = data['item']
    amount = data['amount']

    # Find the customer using the phone number
    customer = Customer.query.filter_by(phone=phone).first()

    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    
    if not is_valid_phone_number(phone):
        return jsonify({'error': 'Invalid phone number format'}), 400

    # Create a new order associated with the customer
    new_order = Order(
        item=item,
        amount=amount,
        customer_id=customer.id  # referencing the customer.id as foreign key
    )

    db.session.add(new_order)
    db.session.commit()

    # Sending SMS alert to the customer
    sms_service = SendSMS()
    try:
        message = f"Hello {customer.name}, your order for {new_order.item} has been placed successfully."
        sms_service.send_message([customer.phone], message)
    except Exception as e:
        print(f"Failed to send SMS: {e}")

    return jsonify({"message": "Order created successfully"}), 201

# API to get specific customer's order statement
@app.route('/api/order/<phone>', methods=['GET'])
def get_order_by_phone(phone):
    # Check if the customer exists based on phone number
    customer = Customer.query.filter_by(phone=phone).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404

    # Retrieve all orders for the customer
    orders = Order.query.filter_by(customer_id=customer.id).all()

    if not orders:
        return jsonify({'message': 'No orders found for this customer'}), 404

    # Format orders into a list of dictionaries
    order_list = [{
        'order_id': order.id,
        'item': order.item,
        'amount': order.amount,
        'created_at': order.time.strftime('%Y-%m-%d %H:%M:%S')
    } for order in orders]

    return jsonify({
        'customer_name': customer.name,
        'phone': customer.phone,
        'orders': order_list
    }), 200


# Retrieve orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    res = [
        {
            'item': order.item,
            'amount': order.amount,
            'time': order.time,
            'customer': order.customer.name,
            "phone": order.customer.phone
        } for order in orders
    ]
        
    return jsonify(res), 200

REDIRECT_URI = "http://localhost:5000/google/auth/"

@app.route('/google/login')
def google_login():
    # Google OAuth configuration
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
        redirect_uri=url_for('google_auth', _external=True)
    )
    
    # Generate the authorization URL
    authorization_url, state = flow.authorization_url(access_type='offline')
    
    # Store the state in the session to verify the response later
    session['state'] = state
    
    # Redirect the user to Google's OAuth 2.0 authorization server
    return redirect(authorization_url)

@app.route('/google/auth/', methods=['POST'])
def google_auth():
    # Verify that the state exists in the session to prevent CSRF attacks
    if 'state' not in session:
        return redirect(url_for('google_login'))

    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
        state=session['state'],
        redirect_uri=url_for('google_auth', _external=True)  # Match the redirect URI exactly
    )

    try:
        # Fetch the token using the authorization response from Google
        flow.fetch_token(authorization_response=request.url)
        # Get the credentials and store them in session
        credentials = flow.credentials
        session['credentials'] = credentials_to_dict(credentials)

        # Redirect to the page
        return redirect(url_for('get_customers'))

    except ValueError as e:
        # Clear the session if the token verification fails
        session.clear()
        return redirect(url_for('google_login'))

    except InvalidGrantError as e:
        # Handle InvalidGrantError by clearing the session
        session.clear()
        return redirect(url_for('google_login'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
