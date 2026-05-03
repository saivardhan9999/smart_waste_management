"""
Grad-CAM implementation for Explainable AI
"""

import numpy as np
import tensorflow as tf
from PIL import Image
import cv2
from app.config import Config


class GradCAM:
    """Grad-CAM for visualizing important regions in waste classification"""
    
    def __init__(self, model, class_names):
        self.model = model
        self.class_names = class_names
        
        # Find last convolutional layer (for MobileNetV2 it's typically the last layer before global pooling)
        self.target_layer = None
        for layer in reversed(self.model.layers):
            if 'conv' in layer.name.lower() or 'depthwise' in layer.name.lower():
                self.target_layer = layer
                break
        
        if self.target_layer is None:
            # Fallback to second to last layer
            self.target_layer = self.model.layers[-2]
        
        # Create a model that outputs both predictions and gradients
        self.gradient_model = tf.keras.Model(
            inputs=[self.model.inputs],
            outputs=[self.target_layer.output, self.model.output]
        )
    
    def generate_heatmap(self, image, predicted_class=None):
        """Generate Grad-CAM heatmap overlay"""
        # Preprocess image
        img_array = self.preprocess_for_model(image)
        
        # Get gradients
        with tf.GradientTape() as tape:
            conv_outputs, predictions = self.gradient_model(img_array)
            predictions = predictions[0]
            
            # Use predicted class if not specified
            if predicted_class is None:
                predicted_idx = tf.argmax(predictions)
            else:
                predicted_idx = self.class_names.index(predicted_class)
            
            loss = predictions[predicted_idx]
        
        # Compute gradients
        grads = tape.gradient(loss, conv_outputs)
        
        # Compute importance weights
        weights = tf.reduce_mean(grads, axis=(0, 1, 2))
        
        # Generate heatmap
        heatmap = tf.reduce_sum(weights * conv_outputs, axis=-1)
        heatmap = np.maximum(heatmap, 0)
        
        # Normalize
        heatmap = heatmap.numpy()[0]
        heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min() + 1e-7)
        
        # Resize heatmap to original image size
        heatmap_resized = cv2.resize(heatmap, (image.width, image.height))
        
        # Convert to 0-255
        heatmap_int = (heatmap_resized * 255).astype(np.uint8)
        
        # Apply colormap
        heatmap_colored = cv2.applyColorMap(heatmap_int, cv2.COLORMAP_JET)
        heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
        
        # Blend with original image
        original_array = np.array(image)
        heatmap_normalized = heatmap_resized[..., np.newaxis]
        
        # Overlay heatmap
        overlayed = original_array * 0.5 + heatmap_colored * 0.5
        overlayed = np.clip(overlayed, 0, 255).astype(np.uint8)
        
        return Image.fromarray(overlayed)
    
    def preprocess_for_model(self, image):
        """Preprocess image for model - consistent with predictor"""
        # Ensure RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize using same method as predictor (LANCZOS)
        # Use Resampling.LANCZOS for Pillow 10+, fallback to LANCZOS for older versions
        try:
            resize_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resize_filter = Image.LANCZOS
        img_resized = image.resize(Config.IMG_SIZE, resize_filter)
        img_array = np.array(img_resized, dtype=np.float32)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

