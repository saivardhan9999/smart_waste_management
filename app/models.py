"""
SQLAlchemy models for Smart Waste Management System
"""

from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize db
db = SQLAlchemy()

# Import Config after db is defined
from app.config import Config


class User(UserMixin, db.Model):
    """User model for admin authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class DetectionLog(db.Model):
    """Model for logging waste classification detections"""
    __tablename__ = 'detection_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(255), nullable=False)
    predicted_class = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # 'good', 'bad', 'worse', 'far_from_saving'
    location_name = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    detection_method = db.Column(db.String(20), nullable=False)  # 'upload' or 'camera'
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DetectionLog {self.predicted_class} ({self.confidence:.2f}) at {self.location_name}>'


class Contact(db.Model):
    """Model for storing contact form submissions"""
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.name} ({self.email})>'


def create_admin_user():
    """Create default admin user if it doesn't exist"""
    admin = User.query.filter_by(username=Config.ADMIN_USERNAME).first()
    if not admin:
        admin = User(username=Config.ADMIN_USERNAME, is_admin=True)
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{Config.ADMIN_USERNAME}' created successfully")
    return admin

