from werkzeug.utils import secure_filename
import os
from flask import current_app
from app import db
from app.models import Orders

class OrderController:
    
    @staticmethod 
    def get_all_Order(page=1, per_page=10): # chercher toutes les commanes
        return Orders.query.order_by(Orders.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )