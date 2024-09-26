'''
Main application initialization
'''
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from api.v1.views import app_views
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.register_blueprint(app_views)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)