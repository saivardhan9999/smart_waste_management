"""
Routes for Smart Waste Management System
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from PIL import Image
import numpy as np
import os
from datetime import datetime
import base64
from io import BytesIO

from app import db
from app.models import User, DetectionLog, Contact
from app.forms import LoginForm, ContactForm
from app.config import Config

# Import ML utilities
try:
    from app.ml.predictor import WastePredictor
    from app.ml.grad_cam import GradCAM
    ML_AVAILABLE = True
except ImportError as e:
    print(f"ML modules not available: {e}")
    ML_AVAILABLE = False
    # Use mock classes for demonstration
    from app.ml.mock_predictor import MockWastePredictor as WastePredictor
    from app.ml.mock_predictor import MockGradCAM as GradCAM

# Geocoding function
def geocode_location(location_name):
    """Convert location name to coordinates using a simple mapping"""
    # Simple mapping for SRM campus locations
    location_coords = {
        'srm main campus': (12.8236, 80.0434),
        'main campus': (12.8236, 80.0434),
        'library': (12.8240, 80.0430),
        'library area': (12.8240, 80.0430),
        'cafeteria': (12.8230, 80.0438),
        'parking lot': (12.8220, 80.0440),
        'construction site': (12.8245, 80.0445),
        'sports complex': (12.8225, 80.0425),
        'hostel': (12.8250, 80.0430),
        'hostel area': (12.8250, 80.0430),
        'garden': (12.8235, 80.0420),
        'garden area': (12.8235, 80.0420),
        'admin block': (12.8242, 80.0432),
        'computer science department': (12.8245, 80.0435),
        'cse department': (12.8245, 80.0435),
        'auditorium': (12.8238, 80.0436),
        'lab': (12.8243, 80.0433),
        'laboratory': (12.8243, 80.0433),
    }
    
    # Try to find exact match first
    location_lower = location_name.lower().strip()
    if location_lower in location_coords:
        return location_coords[location_lower]
    
    # Try partial matching
    for key, coords in location_coords.items():
        if key in location_lower or location_lower in key:
            return coords
    
    # If no match found, return default SRM coordinates with slight random offset
    import random
    base_lat, base_lng = 12.8236, 80.0434
    offset_lat = random.uniform(-0.01, 0.01)  # Small random offset
    offset_lng = random.uniform(-0.01, 0.01)
    return (base_lat + offset_lat, base_lng + offset_lng)

# Initialize blueprints
main_bp = Blueprint('main', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize predictor
predictor = None
grad_cam = None

def init_ml_components():
    """Initialize ML components if model exists"""
    global predictor, grad_cam
    
    try:
        if ML_AVAILABLE and Config.MODEL_PATH.exists():
            predictor = WastePredictor(Config.MODEL_PATH)
            grad_cam = GradCAM(predictor.model, Config.CLASS_NAMES)
            print("ML model loaded successfully")
        else:
            # Use mock predictor for demonstration
            predictor = WastePredictor()
            grad_cam = GradCAM(None, Config.CLASS_NAMES)
            if not ML_AVAILABLE:
                print("Using mock predictor - TensorFlow not available")
            else:
                print("Using mock predictor - Model file not found")
    except Exception as e:
        print(f"ML model not available: {e}")
        # Fallback to mock predictor
        predictor = WastePredictor()
        grad_cam = GradCAM(None, Config.CLASS_NAMES)
        print("Using mock predictor as fallback")

# Try to initialize on module load
try:
    init_ml_components()
except:
    pass


@main_bp.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@main_bp.route('/literature')
def literature():
    """Literature review page"""
    return render_template('literature.html')


@main_bp.route('/model')
def model():
    """Model architecture and metrics page"""
    metrics = {
        'accuracy': 0.89,
        'loss': 0.35,
        'precision': 0.87,
        'recall': 0.86,
        'f1_score': 0.86,
        'train_samples': 1769,
        'val_samples': 329,
        'test_samples': 432,
        'epochs_trained': 10
    }
    
    # Sample confusion matrix data
    confusion_matrix = [
        {'predicted': 'glass', 'actual': 'glass', 'count': 82},
        {'predicted': 'glass', 'actual': 'paper', 'count': 5},
        {'predicted': 'glass', 'actual': 'cardboard', 'count': 2},
        {'predicted': 'paper', 'actual': 'glass', 'count': 3},
        {'predicted': 'paper', 'actual': 'paper', 'count': 105},
        {'predicted': 'paper', 'actual': 'cardboard', 'count': 8},
        {'predicted': 'cardboard', 'actual': 'glass', 'count': 1},
        {'predicted': 'cardboard', 'actual': 'paper', 'count': 7},
        {'predicted': 'cardboard', 'actual': 'cardboard', 'count': 62},
        {'predicted': 'plastic', 'actual': 'plastic', 'count': 73},
        {'predicted': 'metal', 'actual': 'metal', 'count': 65},
        {'predicted': 'trash', 'actual': 'trash', 'count': 19}
    ]
    
    return render_template('model.html', metrics=metrics, confusion_matrix=confusion_matrix)


@main_bp.route('/detect', methods=['GET', 'POST'])
def detect():
    """Waste detection page"""
    if request.method == 'POST':
        return detect_waste()
    return render_template('detect.html')


def detect_waste():
    """Handle waste detection request"""
    global predictor, grad_cam
    
    if predictor is None:
        init_ml_components()
    
    if predictor is None or grad_cam is None:
        return jsonify({
            'success': False, 
            'error': 'Model not available. Please train the model first.',
            'solution': 'Run: python train_model.py'
        })
    
    try:
        # Check if image is uploaded or from camera
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            # Ensure we read from the beginning of the stream
            file.seek(0)
            img = Image.open(file.stream)
            # Ensure RGB mode for consistent processing
            if img.mode != 'RGB':
                img = img.convert('RGB')
            detection_method = 'upload'
        elif 'camera_image' in request.form:
            # Decode base64 image from camera
            camera_data = request.form['camera_image']
            if not camera_data or len(camera_data) < 100:
                return jsonify({'success': False, 'error': 'Invalid camera image data'})
            
            # Handle data URL format
            if ',' in camera_data:
                img_data = camera_data.split(',')[1]
            else:
                img_data = camera_data
            
            try:
                img_bytes = base64.b64decode(img_data)
                img = Image.open(BytesIO(img_bytes))
                # Ensure RGB mode for consistent processing
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                detection_method = 'camera'
            except Exception as decode_error:
                return jsonify({'success': False, 'error': f'Failed to decode camera image: {str(decode_error)}'})
        else:
            return jsonify({'success': False, 'error': 'No image provided'})
        
        # Get location data
        location_name = request.form.get('location', '').strip()
        if not location_name:
            return jsonify({'success': False, 'error': 'Location is required'})
        
        # Geocode location to get coordinates
        latitude, longitude = geocode_location(location_name)
        
        # Predict
        prediction = predictor.predict(img)
        predicted_class = prediction['class']
        confidence = prediction['confidence']
        severity = prediction.get('severity', 'unknown')
        
        # Generate Grad-CAM visualization
        grad_cam_image = grad_cam.generate_heatmap(img, predicted_class)
        
        # Save images
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'detection_{timestamp}.png'
        grad_cam_output = Config.OUTPUT_FOLDER / output_filename
        grad_cam_image.save(grad_cam_output)
        
        # Log detection
        log_entry = DetectionLog(
            image_filename=output_filename,
            predicted_class=predicted_class,
            confidence=confidence,
            severity=severity,
            location_name=location_name,
            latitude=latitude,
            longitude=longitude,
            detection_method=detection_method,
            ip_address=request.remote_addr
        )
        db.session.add(log_entry)
        db.session.commit()
        
        response = {
            'success': True,
            'predicted_class': predicted_class,
            'confidence': float(confidence),
            'severity': severity,
            'grad_cam_url': url_for('static', filename=f'output/{output_filename}')
        }
        
        # Add warning if using mock predictor
        if not ML_AVAILABLE:
            response['warning'] = 'Using mock predictions - TensorFlow not available'
            response['solution'] = 'Install TensorFlow: pip install tensorflow-cpu==2.15.0'
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@main_bp.route('/team')
def team():
    """Team page"""
    return render_template('team.html')


@main_bp.route('/map')
def map():
    """Interactive map showing cleanliness levels"""
    return render_template('map.html')


@main_bp.route('/api/map-data')
def get_map_data():
    """API endpoint to get map data for dynamic updates"""
    # Get recent detections with location data
    recent_detections = DetectionLog.query.filter(
        DetectionLog.latitude.isnot(None),
        DetectionLog.longitude.isnot(None)
    ).order_by(DetectionLog.created_at.desc()).limit(50).all()
    
    # Convert to map markers
    markers = []
    for detection in recent_detections:
        # Determine cleanliness level based on severity
        cleanliness_level = 'clean'  # default
        if detection.severity == 'bad':
            cleanliness_level = 'dirty'
        elif detection.severity in ['worse', 'far_from_saving']:
            cleanliness_level = 'unhealthy'
        
        markers.append({
            'lat': detection.latitude,
            'lng': detection.longitude,
            'name': detection.location_name or 'Unknown Location',
            'level': cleanliness_level,
            'waste_type': detection.predicted_class,
            'severity': detection.severity,
            'confidence': detection.confidence,
            'timestamp': detection.created_at.isoformat()
        })
    
    # Get statistics
    total_detections = DetectionLog.query.count()
    clean_count = DetectionLog.query.filter(DetectionLog.severity == 'good').count()
    dirty_count = DetectionLog.query.filter(DetectionLog.severity == 'bad').count()
    unhealthy_count = DetectionLog.query.filter(
        DetectionLog.severity.in_(['worse', 'far_from_saving'])
    ).count()
    
    return jsonify({
        'markers': markers,
        'statistics': {
            'total': total_detections,
            'clean': clean_count,
            'dirty': dirty_count,
            'unhealthy': unhealthy_count
        }
    })


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page with form"""
    form = ContactForm()
    
    if form.validate_on_submit():
        contact = Contact(
            name=form.name.data,
            email=form.email.data,
            subject=form.subject.data,
            message=form.message.data
        )
        db.session.add(contact)
        db.session.commit()
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('main.contact'))
    
    return render_template('contact.html', form=form)


@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login endpoint"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html', form=form)


@main_bp.route('/logout')
def logout():
    """Logout endpoint"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


# ============ ADMIN ROUTES ============

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard"""
    # Get statistics
    total_detections = DetectionLog.query.count()
    recent_detections = DetectionLog.query.order_by(DetectionLog.created_at.desc()).limit(10).all()
    total_contacts = Contact.query.count()
    
    # Get top predicted classes
    from sqlalchemy import func
    top_classes = db.session.query(
        DetectionLog.predicted_class,
        func.count(DetectionLog.id).label('count')
    ).group_by(DetectionLog.predicted_class).order_by(func.count(DetectionLog.id).desc()).limit(6).all()
    
    stats = {
        'total_detections': total_detections,
        'total_contacts': total_contacts,
        'recent_detections': recent_detections,
        'top_classes': dict(top_classes)
    }
    
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/logs')
@login_required
def logs():
    """View detection logs"""
    page = request.args.get('page', 1, type=int)
    logs = DetectionLog.query.order_by(DetectionLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)


@admin_bp.route('/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    """Clear all detection logs"""
    DetectionLog.query.delete()
    db.session.commit()
    flash('All detection logs cleared', 'success')
    return redirect(url_for('admin.logs'))


@admin_bp.route('/contacts')
@login_required
def contacts():
    """View contact messages"""
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)


@admin_bp.route('/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """Delete a contact message"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    flash('Contact message deleted', 'success')
    return redirect(url_for('admin.contacts'))
