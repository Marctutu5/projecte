from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
import os

db = SQLAlchemy()

# Modelos
class products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    photo = db.Column(db.String)
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created = db.Column(DateTime, default=db.func.current_timestamp())
    updated = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

class categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    slug = db.Column(db.String, unique=True)
    products = db.relationship('products', backref='category', lazy=True)
