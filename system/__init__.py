import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
oauth = OAuth(app)

login_manager = LoginManager(app)
login_manager.login_view = 'google'
login_manager.login_message_category = 'info'


from system import routes