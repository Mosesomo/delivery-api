'''
script for managing the database
'''
from system import app, db
from system.model import Customer, User, Order


with app.app_context():
    db.create_all()
