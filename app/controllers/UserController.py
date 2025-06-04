from werkzeug.utils import secure_filename
import os
from flask import current_app
from app import db
from app.models import User

class UserController:
    
    @staticmethod 
    def get_all_user(page=1, per_page=10): # chercher toutes les users
        return User.query.order_by().paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )