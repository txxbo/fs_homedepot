from scraper import db
from datetime import datetime


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(), index=True, unique=True)
    title = db.Column(db.String, default="New Product")
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_check = db.Column(db.DateTime, default=datetime.utcnow)
    url = db.Column(db.String, index=True, unique=True)
    enabled = db.Column(db.Boolean, default=True)
    availability = db.Column(db.Boolean)
    notify = db.Column(db.Boolean)
    price = db.Column(db.Float)
