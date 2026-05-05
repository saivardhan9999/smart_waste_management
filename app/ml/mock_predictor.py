"""
Mock predictor for demonstration when TensorFlow is not available
"""

import random
from PIL import Image
import numpy as np


class MockWastePredictor:
    """Mock class for waste classification when TensorFlow is not available"""
    
    def __init__(self, model_path=None):
        """Initialize mock predictor"""
        self.class_names = ['glass', 'paper', 'cardboard', 'plastic', 'metal', 'trash']
        self.img_size = (224, 224)
        print("Using MockWastePredictor - TensorFlow not available")
    
    def preprocess_image(self, image):
        """Mock preprocess image"""
        # Just resize the image
        image = image.resize(self.img_size)
        return image
    
    def predict(self, image):
        """Make mock prediction on image"""
        # Preprocess
        img = self.preprocess_image(image)
        
        # Generate more realistic predictions with higher confidence
        predictions = np.random.random(len(self.class_names))
        
        # Add more bias to make predictions more confident
        predictions[0] += 0.3  # glass
        predictions[1] += 0.4  # paper  
        predictions[2] += 0.35  # cardboard
        predictions[3] += 0.45  # plastic
        predictions[4] += 0.3   # metal
        predictions[5] += 0.2   # trash
        
        # Normalize
        predictions = predictions / np.sum(predictions)
        
        predicted_index = np.argmax(predictions)
        confidence = predictions[predicted_index]
        
        # Boost confidence to more realistic levels (70-95%)
        confidence = min(0.95, max(0.70, confidence + 0.3))
        
        predicted_class = self.class_names[predicted_index]
        
        # Determine waste severity based on class and confidence
        severity = self._determine_severity(predicted_class, confidence)
        
        return {
            'class': predicted_class,
            'confidence': float(confidence),
            'severity': severity,
            'all_predictions': {self.class_names[i]: float(predictions[i]) for i in range(len(self.class_names))}
        }
    
    def _determine_severity(self, waste_class, confidence):
        """Determine waste severity based on class and confidence"""
        # Define severity levels
        severity_levels = {
            'glass': {'good': 0.8, 'bad': 0.6, 'worse': 0.4, 'far_from_saving': 0.2},
            'paper': {'good': 0.7, 'bad': 0.5, 'worse': 0.3, 'far_from_saving': 0.1},
            'cardboard': {'good': 0.75, 'bad': 0.55, 'worse': 0.35, 'far_from_saving': 0.15},
            'plastic': {'good': 0.6, 'bad': 0.4, 'worse': 0.25, 'far_from_saving': 0.1},
            'metal': {'good': 0.7, 'bad': 0.5, 'worse': 0.3, 'far_from_saving': 0.1},
            'trash': {'good': 0.3, 'bad': 0.2, 'worse': 0.1, 'far_from_saving': 0.05}
        }
        
        thresholds = severity_levels.get(waste_class, severity_levels['trash'])
        
        if confidence >= thresholds['good']:
            return 'good'
        elif confidence >= thresholds['bad']:
            return 'bad'
        elif confidence >= thresholds['worse']:
            return 'worse'
        else:
            return 'far_from_saving'


class MockGradCAM:
    """Mock GradCAM for demonstration when TensorFlow is not available"""
    
    def __init__(self, model, class_names):
        """Initialize mock GradCAM"""
        self.class_names = class_names
        print("Using MockGradCAM - TensorFlow not available")
    
    def generate_heatmap(self, image, predicted_class):
        """Generate mock heatmap"""
        # Create a simple mock heatmap by adding some colored overlay
        import numpy as np
        from PIL import Image, ImageDraw
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Create a simple overlay pattern
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Draw some random rectangles to simulate attention areas
        for _ in range(5):
            x1 = random.randint(0, image.width // 2)
            y1 = random.randint(0, image.height // 2)
            x2 = x1 + random.randint(20, 80)
            y2 = y1 + random.randint(20, 80)
            
            # Use different colors based on predicted class
            colors = {
                'glass': (0, 255, 255, 100),      # Cyan
                'paper': (255, 255, 0, 100),      # Yellow
                'cardboard': (139, 69, 19, 100), # Brown
                'plastic': (255, 0, 255, 100),    # Magenta
                'metal': (192, 192, 192, 100),   # Silver
                'trash': (128, 128, 128, 100)    # Gray
            }
            
            color = colors.get(predicted_class, (255, 0, 0, 100))
            draw.rectangle([x1, y1, x2, y2], fill=color)
        
        # Convert back to RGB
        result = Image.alpha_composite(image.convert('RGBA'), overlay).convert('RGB')
        
        return result
