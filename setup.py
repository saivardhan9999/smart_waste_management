"""
Setup script for Smart Waste Management System
This script helps install dependencies and set up the environment properly
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version is not compatible. Please use Python 3.8 or higher")
        return False

def install_tensorflow():
    """Install TensorFlow with proper version for Windows"""
    print("\n🔧 Installing TensorFlow...")
    
    # Try different TensorFlow versions for Windows compatibility
    tensorflow_versions = [
        "tensorflow-cpu==2.15.0",  # Most stable for Windows
        "tensorflow-cpu==2.14.0",  # Alternative
        "tensorflow-cpu",          # Latest
    ]
    
    for version in tensorflow_versions:
        print(f"\n🔄 Trying to install {version}...")
        if run_command(f"pip install {version}", f"Installing {version}"):
            # Test if TensorFlow can be imported
            test_command = "python -c \"import tensorflow as tf; print('TensorFlow version:', tf.__version__)\""
            if run_command(test_command, f"Testing {version}"):
                print(f"✅ {version} installed and working!")
                return True
            else:
                print(f"⚠️ {version} installed but not working properly")
        else:
            print(f"❌ Failed to install {version}")
    
    print("❌ All TensorFlow installation attempts failed")
    return False

def install_other_dependencies():
    """Install other required dependencies"""
    print("\n📦 Installing other dependencies...")
    
    dependencies = [
        "Flask==3.0.0",
        "Flask-Login==0.6.3", 
        "Flask-Migrate==4.0.5",
        "Flask-WTF==1.2.1",
        "SQLAlchemy==2.0.23",
        "Werkzeug==3.0.1",
        "WTForms==3.1.1",
        "Pillow>=10.0.0",
        "numpy>=1.26.0",
        "opencv-python==4.8.1.78"
    ]
    
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"⚠️ Failed to install {dep}, continuing...")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "uploads",
        "static/output",
        "instance"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def test_model_training():
    """Test if model can be trained"""
    print("\n🧠 Testing model training...")
    
    if run_command("python train_model.py", "Training model"):
        print("✅ Model training completed successfully!")
        return True
    else:
        print("⚠️ Model training failed, but mock predictor will be used")
        return False

def main():
    """Main setup function"""
    print("🚀 Smart Waste Management System Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    install_other_dependencies()
    
    # Install TensorFlow
    tensorflow_success = install_tensorflow()
    
    # Create directories
    create_directories()
    
    # Test model training
    if tensorflow_success:
        test_model_training()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    
    if tensorflow_success:
        print("✅ TensorFlow is working properly")
        print("✅ You can now run: python run.py")
    else:
        print("⚠️ TensorFlow installation failed")
        print("✅ The application will use mock predictions")
        print("✅ You can still run: python run.py")
        print("\n💡 To fix TensorFlow issues:")
        print("   1. Try: pip install tensorflow-cpu==2.15.0")
        print("   2. Or use conda: conda install tensorflow")
        print("   3. Or use a virtual environment with Python 3.10")

if __name__ == "__main__":
    main()




