'''User model for managing orders'''
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    oauth_provider = db.Column(db.String(50), nullable=False, default='google')
    oauth_id = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # user or admin

    def __repr__(self):
        return f"<User {self.username}>"
