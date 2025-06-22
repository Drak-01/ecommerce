from flask import Flask
from .models import db, User 
from flask_migrate import Migrate
import os
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)
    
    # Configuration de base
    app.config["SECRET_KEY"] = "pojpqdd@@dqsd/**sd"  # À changer en production!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://draken:123@localhost/ecommerce'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    csrf = CSRFProtect(app)
    
    # Configuration pour les uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'products')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Initialisation de la base de données
    db.init_app(app)
    
    # Initialisation de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login" 
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Création des tables et dossier d'upload
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialisation de Flask-Migrate
    migrate = Migrate(app, db)
    
    #blueprints
    from app.routes import main_routes, admin_bp
    app.register_blueprint(main_routes)
    app.register_blueprint(admin_bp)
    
    return app