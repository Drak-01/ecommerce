from datetime import datetime
import logging
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from flask import flash, current_app
from flask_login import login_user
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from ..models import db, User
from ..forms import LoginForm

logger = logging.getLogger(__name__)

class UserController:
    
    @staticmethod 
    def get_all_users(page=1, per_page=10):
        """Récupère tous les utilisateurs paginés avec gestion des erreurs"""
        try:
            return User.query.order_by(User.username.asc()).paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
        except SQLAlchemyError as e:
            logger.error(f"Erreur base de données: {str(e)}")
            return None
    
    @staticmethod
    def login(form):
        """Connexion standard sécurisée"""
        try:
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user or not check_password_hash(user.password_hash, form.password.data):
                flash("Identifiants incorrects", 'danger')
                return False, None
                
            if not user.is_active:  # Ajout d'un champ is_active pour désactiver des comptes
                flash("Ce compte est désactivé", 'warning')
                return False, None
                
            login_user(user, remember=form.remember.data)
            logger.info(f"Connexion réussie pour {user.email}")
            return True, user
            
        except SQLAlchemyError as e:
            logger.error(f"Erreur DB lors de la connexion: {str(e)}")
            flash("Erreur technique lors de la connexion", 'danger')
            return False, None
    @staticmethod
    def register(form):
        """Inscription sécurisée avec validation complète"""
        try:
            # Validation préalable
            if not form.validate():
                flash("Veuillez corriger les erreurs dans le formulaire", 'danger')
                return False

            if User.query.filter(func.lower(User.username) == func.lower(form.username.data.strip())).first():
                flash("Ce nom d'utilisateur est déjà pris", 'warning')
                return False

            if User.query.filter(func.lower(User.email) == form.email.data.strip().lower()).first():
                flash("Cet email est déjà utilisé", 'warning')
                return False

            if len(form.password.data) < 8:
                flash("Le mot de passe doit contenir au moins 8 caractères", 'danger')
                return False

            user = User(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password(form.password.data)  

            db.session.add(user)
            db.session.commit()

            logger.info(f"Nouvel utilisateur #{user.id} enregistré: {user.email}")
            flash('Inscription réussie! Un email de confirmation a été envoyé.', 'success')
            
            # Envoyer un email de confirmation (optionnel)
            #send_confirmation_email(user)
            
            return True, user

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Erreur d'intégrité DB: {str(e.orig)}", exc_info=True)
            flash("Une erreur est survenue lors de l'inscription", 'danger')
            return False

        except SQLAlchemyError as e:
            db.session.rollback()
            logger.critical(f"Erreur DB critique: {str(e)}", exc_info=True)
            flash("Une erreur technique est survenue", 'danger')
            return False

        except Exception as e:
            db.session.rollback()
            logger.exception("Erreur inattendue lors de l'inscription")
            flash("Une erreur inattendue est survenue", 'danger')
            return False
        
    @staticmethod
    def login_admin(form):
        """Connexion admin sécurisée avec journalisation"""
        try:
            user = User.query.filter_by(email=form.email.data).first()
            
            # Validation en une étape
            valid = (user and 
                    check_password_hash(user.password_hash, form.password.data) and 
                    getattr(user, 'is_admin', False))
            
            if not valid:
                logger.warning(f"Tentative de connexion admin échouée pour {form.email.data}")
                flash("Accès refusé: identifiants invalides ou privilèges insuffisants", 'danger')
                return False, None
                
            login_user(user)
            logger.info(f"Connexion admin réussie pour {user.email}")
            return True, user
            
        except SQLAlchemyError as e:
            logger.critical(f"Erreur DB connexion admin: {str(e)}")
            flash("Erreur système - Veuillez réessayer plus tard", 'danger')
            return False, None
            
        except Exception as e:
            logger.exception("Erreur inattendue lors de la connexion admin")
            flash("Erreur technique critique", 'danger')
            return False, None
        
    @staticmethod
    def get_user_email(email):
        return (
            User.query.filter_by(email=email).first()
        )
    
    @staticmethod
    def get_user_by_id(id):
        return (
            User.query.filter_by(id=id).first()
        )
    
    @staticmethod
    def deleteUser(id):        
        admin  = User.query.filter_by(is_admin=1).count()
        if admin >= 1:
            user = User.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()
            return True
        else:
            return False
        
    @staticmethod
    def user_count():
        return len(User.query.all())
