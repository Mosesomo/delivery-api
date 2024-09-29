from system import app, db
from system.model import Customer, Order
import unittest

class CustomerOrderTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test variables and push application context."""
        self.app = app
        self.client = self.app.test_client()

        # Push the application context
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create all the tables for testing
        db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        db.session.remove()
        db.drop_all()

        # Pop the application context
        self.app_context.pop()

    def test_create_customer(self):
        """Test API to create a customer."""
        customer_data = {
            'name': 'Jane Doe',
            'phone': '+254701234567'
        }

        response = self.client.post('/api/customer', json=customer_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'customer created successfully', response.data)

    def test_get_customers(self):
        """Test API to retrieve customers."""
        # First, create a customer
        customer = Customer(name='Jane Doe', phone='+254701234567')
        db.session.add(customer)
        db.session.commit()

        # Get all customers
        response = self.client.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Jane Doe', response.data)

    def test_create_order(self):
        """Test API to create an order for a customer."""
        # First, create a customer
        customer = Customer(name='John Doe', phone='+254700000000')
        db.session.add(customer)
        db.session.commit()

        # Create order data using the existing customer
        order_data = {
            'item': 'Laptop',
            'amount': 1200,
            'customer_id': customer.id,
        }

        response = self.client.post('/api/order', json=order_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Order created successfully', response.data)

    def test_get_orders(self):
        """Test API to retrieve orders."""
        # First, create a customer and an order
        customer = Customer(name='John Doe', phone='+254700000000')
        db.session.add(customer)
        db.session.commit()

        order = Order(item='Laptop', amount=1200, customer_id=customer.id)
        db.session.add(order)
        db.session.commit()

        # Get all orders
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Laptop', response.data)


if __name__ == '__main__':
    unittest.main()
