"""
Tutoring School Management System - Production Application Factory

This module creates and configures the Flask application for production use.
It implements the Application Factory pattern for better modularity and testing.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)


def create_app(config_object=None):
    """
    Application factory function to create and configure the Flask app.
    
    Args:
        config_object: Optional configuration object to override defaults
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    if config_object:
        app.config.from_object(config_object)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure Sentry for error tracking (production only)
    if app.config.get('SENTRY_DSN') and not app.debug:
        sentry_sdk.init(
            dsn=app.config['SENTRY_DSN'],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
            release=f"tutoring-school@{app.config.get('VERSION', '1.0.0')}"
        )
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup login manager
    setup_login_manager(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def setup_logging(app):
    """Configure logging for the application."""
    if not app.debug:
        # File handler for production
        file_handler = RotatingFileHandler(
            'logs/tutoring_school.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        console_handler.setLevel(logging.INFO)
        app.logger.addHandler(console_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Tutoring School application startup')


def register_blueprints(app):
    """Register all blueprints for the application."""
    from app.blueprints.auth import auth_bp
    from app.blueprints.parent import parent_bp
    from app.blueprints.teacher import teacher_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(parent_bp, url_prefix='/parent')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register main routes
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)


def register_error_handlers(app):
    """Register error handlers for the application."""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f'Page not found: {request.url}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server error: {error}')
        return render_template('errors/500.html'), 500


def setup_login_manager(app):
    """Configure login manager."""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'กรุณาเข้าสู่ระบบเพื่อใช้งานหน้านี้'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))


# Import models to ensure they're registered with SQLAlchemy
from app import models
