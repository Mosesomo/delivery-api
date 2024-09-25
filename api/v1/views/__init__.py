'''
(package) Importing blueprints for customers, auth and order management
'''
from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='api/v1')


from api.v1.views.customer import *
from api.v1.views.order import *
from api.v1.views.auth import *