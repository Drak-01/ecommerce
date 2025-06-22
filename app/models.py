from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash


db = SQLAlchemy()

class User(UserMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(300))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'product' 
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('Category', backref='products')
    
    @property
    def image_url(self):
        if self.image:
            return url_for('static', filename=f'uploads/products/{self.image}', _external=True)
        return None

class Orders(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  
    user = db.relationship('User', backref='orders')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Orders', backref='items')  
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  
    product = db.relationship('Product')
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float)