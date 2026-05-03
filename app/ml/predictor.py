"""
Waste prediction module using MobileNetV2
"""

import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras
import os
from app.config import Config

# Set TensorFlow to use deterministic operations for consistent predictions
os.environ['TF_DETERMINISTIC_OPS'] = '1'
os.environ['PYTHONHASHSEED'] = '0'

# Configure TensorFlow for reproducibility
try:
    # TensorFlow 2.8+ has enable_op_determinism
    if hasattr(tf.config.experimental, 'enable_op_determinism'):
        tf.config.experimental.enable_op_determinism()
    # For older versions, set seed
    tf.random.set_seed(42)
    np.random.seed(42)
except Exception as e:
    print(f"Warning: Could not set TensorFlow deterministic operations: {e}")
    # Fallback: set seeds
    tf.random.set_seed(42)
    np.random.seed(42)


class WastePredictor:
    """Class for waste classification using trained model"""
    
    def __init__(self, model_path):
        """Load trained model"""
        self.model = keras.models.load_model(str(model_path))
        self.class_names = Config.CLASS_NAMES
        self.img_size = Config.IMG_SIZE
    
    def preprocess_image(self, image):
        """Preprocess image for model input - using consistent preprocessing"""
        # Ensure image is RGB (in case it's not)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize image using LANCZOS for consistent quality
        # This ensures the same interpolation method is always used
        # Use Resampling.LANCZOS for Pillow 10+, fallback to LANCZOS for older versions
        try:
            resize_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resize_filter = Image.LANCZOS
        image = image.resize(self.img_size, resize_filter)
        
        # Convert to array - ensure uint8 format
        img_array = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1] - ensure consistent normalization
        img_array = img_array / 255.0
        
        # Expand dimensions for batch
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    
    def predict(self, image):
        """Make prediction on image"""
        # Preprocess
        img_array = self.preprocess_image(image)
        
        # Predict with deterministic settings
        predictions = self.model.predict(img_array, verbose=0)
        predicted_index = np.argmax(predictions[0])
        confidence = predictions[0][predicted_index]
        
        predicted_class = self.class_names[predicted_index]
        
        return {
            'class': predicted_class,
            'confidence': float(confidence),
            'all_predictions': {self.class_names[i]: float(predictions[0][i]) for i in range(len(self.class_names))}
        }

