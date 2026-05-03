"""
Configuration settings for Smart Waste Management System
"""

import os
from pathlib import Path

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///waste_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # ML Model paths
    BASE_DIR = Path(__file__).parent.parent
    MODEL_DIR = BASE_DIR / 'app' / 'ml'
    MODEL_PATH = MODEL_DIR / 'model.keras'
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    OUTPUT_FOLDER = BASE_DIR / 'static' / 'output'
    
    # Garbage classification paths
    DATA_DIR = BASE_DIR / 'Garbage classification' / 'Garbage classification'
    TRAIN_FILE = BASE_DIR / 'one-indexed-files-notrash_train.txt'
    VAL_FILE = BASE_DIR / 'one-indexed-files-notrash_val.txt'
    TEST_FILE = BASE_DIR / 'one-indexed-files-notrash_test.txt'
    
    # Model configuration
    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32
    EPOCHS = 10
    NUM_CLASSES = 6
    CLASS_NAMES = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']
    
    # Admin credentials (default - should be changed)
    ADMIN_USERNAME = 'admin'
    ADMIN_PASSWORD = 'admin123'
    
    @staticmethod
    def init_app(app):
        """Initialize app-specific configurations"""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
        os.makedirs(Config.MODEL_DIR, exist_ok=True)

