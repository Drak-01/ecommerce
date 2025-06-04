from flask import Flask
from .models import db
from flask_migrate import Migrate
import os

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "pojpqdd@@dqsd/**sd"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://draken:123@localhost/ecommerce'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuration pour les uploads
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'products')
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
    
    db.init_app(app)
    with app.app_context():
        db.create_all()
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        
    migrate = Migrate(app, db)
    
    from app.routes import main_routes, admin_bp
    app.register_blueprint(main_routes)
    app.register_blueprint(admin_bp)

    
    return app
    