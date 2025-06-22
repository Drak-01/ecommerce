from sqlalchemy import and_
from werkzeug.utils import secure_filename
import os
from flask import current_app
from app import db
from app.models import Orders, OrderItem, User

class OrderController:
    
    @staticmethod 
    def get_all_Order(page=1, per_page=10): # chercher toutes les commanes
        return Orders.query.order_by(Orders.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
    @staticmethod
    def get_orders_by_user(user_id):
        return (
            Orders.query
            .filter_by(user_id=user_id)
            .options(db.joinedload(Orders.items).joinedload(OrderItem.product))
            .order_by(Orders.created_at.desc())
            .all()
        )
        
    @staticmethod
    def get_order_by_userid(user_id):
        order = Orders.query.filter_by(user_id=user_id, status='pending').first()
        if not order:
            order = Orders(user_id=user_id, total=0, status='pending')
            db.session.add(order)
            db.session.commit()
        return order
    
    @staticmethod
    def get_order_item(product_id, order_id):
        return (
            OrderItem.query
            .filter(and_(OrderItem.product_id == product_id, OrderItem.order_id == order_id))
            .first()
        )
        
    @staticmethod
    def get_order_id(id):
        return (
            Orders.query.filter_by(id=id).all()
        )
    
    @staticmethod
    def order_count():
        orders = Orders.query.all()
        return len(orders)