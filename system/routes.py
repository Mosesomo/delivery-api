'''
customer route (crud operation)
'''
from flask import request, jsonify
from system.model import Customer, Order
from app import app, db


# create customer
@app.route('/api/customer', methods=['POST'])
def create_customer():
    data = request.get_json()
    new_customer = Customer(
        name=data['name'],
        code=data['code'],
        phone=data['phone']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message": "customer created successfully"}), 201

# Retrieve users
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    results = [{'name': c.name, 'code': c.code, 'phone': c.phone} for c in customers]
    return jsonify(results), 200

# create order
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    customer = Customer.query.filter_by(id=data['customer_id']).first()
    
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    
    new_order = Order(
        item=data['item'],
        amount=data['amount'],
        custom_id=customer.id
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    # sending message alerting customers
    
    return jsonify({"message": "Order created successfully"}), 201

# Retrieve orders
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    res = [
        {'item': order.item, 'amount': order.amount, 'time': order.time, 'customer': order.customer.name } for order in orders
    ]
    
    return jsonify(res), 200
