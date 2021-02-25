from scraper import db, login
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(), index=True, unique=True)
    title = db.Column(db.String, default="New Product")
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_check = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String, index=True, unique=True)
    enabled = db.Column(db.Boolean, default=True)
    availability = db.Column(db.Boolean, default=False)
    notify = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, default=0.0)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    updates_available = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
