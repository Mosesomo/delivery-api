'''
customer route (crud operation)
'''
import os
from flask import request, jsonify, url_for, redirect
from flask_login import login_required, current_user
from system.model import Customer, Order, User
from system import app, db, oauth, login_manager
from system.sms import SendSMS
from system.validate_phone import is_valid_phone_number
from authlib.integrations.flask_client import OAuth


# create customer
@app.route('/api/customer', methods=['POST'])
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
@login_required
def get_customers():
    if current_user.is_authenticated:
        customers = Customer.query.all()
        results = [{"id": c.id, 'name': c.name, 'phone': c.phone} for c in customers]
        return jsonify(results), 200
    return jsonify({"error": "Unauthorized"}), 401

# create order
@app.route('/api/order', methods=['POST'])
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
        'created_at': order.time.strftime('%Y-%m-%d %H:%M:%S')  # Format date as needed
    } for order in orders]

    return jsonify({
        'customer_name': customer.name,
        'phone': customer.phone,
        'orders': order_list
    }), 200


# Retrieve orders
@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    if current_user.is_authenticated:
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
    return jsonify({"error": "Unauthorized"}), 401

@app.route('/google/')
def google():
    # Google OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile',
            'nonce': 'some_nonce_value'
        }
    )

    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token, None)

        google_id = user_info.get('sub')
        email = user_info.get('email')
        username = user_info.get('name', email.split('@')[0])
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User.query.filter_by(email=email).first()
            if user:
                return jsonify({'error': 'Email address already in use. Please log in.'}), 400

            # Create a new user if not found
            user = User(google_id=google_id, username=username, email=email)
            db.session.add(user)
            db.session.commit()

        return jsonify({
            'message': 'Logged in successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except Exception as e:
        print(f"Error during authentication: {e}")
        return jsonify({'error': 'Authentication failed. Please try again.'}), 400
