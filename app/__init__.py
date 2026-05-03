"""
Flask Application Factory for Smart Waste Management System
SRM Institute - E2 ML Project
"""

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

from app.config import Config
from app.models import db, User, DetectionLog, Contact, create_admin_user


login_manager = LoginManager()
migrate = Migrate()


def create_app(config_class=Config):
    """Application factory pattern for Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.admin_login'
    login_manager.login_message = 'Please log in to access the admin dashboard.'
    
    migrate.init_app(app, db)
    
    # Configure login manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import main_bp, admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables and seed admin user
    with app.app_context():
        db.create_all()
        create_admin_user()
    
    return app

