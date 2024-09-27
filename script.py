'''
script for managing the database
'''
from app import app, db
from api.v1.models.customer import *
from api.v1.models.order import *
from api.v1.models.user import *


with app.app_context():
    db.create_all()