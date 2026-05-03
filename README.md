# Smart Waste Management System

A Flask-based web application for waste classification using machine learning.

## Current Status

⚠️ **TensorFlow Installation Issue Detected**

The application is currently running with a **mock predictor** due to TensorFlow DLL loading issues on Windows. This means:

- ✅ The web application works and shows the interface
- ✅ You can upload images and see mock predictions
- ⚠️ Predictions are simulated (not from actual trained model)
- ⚠️ Grad-CAM visualizations are mock overlays

## Quick Fix for TensorFlow

### Option 1: Install Compatible TensorFlow Version
```bash
pip uninstall tensorflow-cpu -y
pip install tensorflow-cpu==2.15.0
```

### Option 2: Use Conda (Recommended)
```bash
conda create -n waste-mgmt python=3.10
conda activate waste-mgmt
conda install tensorflow
```

### Option 3: Use Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install tensorflow-cpu==2.15.0
```

## Running the Application

1. **With Mock Predictor (Current State)**:
   ```bash
   python run.py
   ```
   - Visit: http://localhost:5000
   - Upload images to see mock predictions
   - Warning messages will indicate mock mode

2. **With Real Model (After TensorFlow Fix)**:
   ```bash
   python train_model.py  # Train the model first
   python run.py          # Run the application
   ```

## Features

- 🖼️ Image upload and camera capture
- 🧠 Waste classification (6 categories: glass, paper, cardboard, plastic, metal, trash)
- 🔥 Grad-CAM visualization
- 📊 Admin dashboard with detection logs
- 📧 Contact form
- 👥 Team information

## Project Structure

```
e2_project/
├── app/
│   ├── ml/
│   │   ├── predictor.py      # Real ML predictor
│   │   ├── mock_predictor.py # Mock predictor (fallback)
│   │   ├── grad_cam.py       # Grad-CAM visualization
│   │   └── model.keras       # Trained model (if available)
│   ├── templates/             # HTML templates
│   ├── static/               # CSS, JS, images
│   └── routes.py             # Flask routes
├── Garbage classification/   # Training data
├── train_model.py            # Model training script
├── run.py                    # Application entry point
└── setup.py                  # Setup script
```

## Training Data

The project includes 2,527 images across 6 waste categories:
- Cardboard: 403 images
- Glass: 501 images  
- Metal: 410 images
- Paper: 594 images
- Plastic: 482 images
- Trash: 137 images

## Troubleshooting

### TensorFlow DLL Error
If you see "DLL load failed" errors:
1. Try Python 3.10 instead of 3.13
2. Use conda instead of pip
3. Install Visual C++ Redistributable
4. Use the mock predictor (current setup)

### Model Training Issues
- Ensure all training data files exist
- Check file paths in `train_model.py`
- Verify image file formats (JPG)

### Application Issues
- Check Flask dependencies are installed
- Verify database file permissions
- Check port 5000 is available

## Development

To contribute or modify:
1. Fix TensorFlow installation
2. Train model: `python train_model.py`
3. Test predictions: `python -c "from app.ml.predictor import WastePredictor; ..."`
4. Run application: `python run.py`

## Admin Access

Default credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ Change these in production!**




