"""
Run script for Smart Waste Management System
SRM Institute - E2 ML Project
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("  Smart Waste Management System")
    print("  SRM Institute - E2 ML Project")
    print("=" * 60)
    print("\nStarting Flask application...")
    print("Available at: http://localhost:5000")
    print("Default Admin: admin / admin123")
    print("\nPress CTRL+C to stop")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

