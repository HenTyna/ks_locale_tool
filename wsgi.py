#!/usr/bin/env python3
"""
WSGI entry point for Railway
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app
from api.app import app

# This is what Railway will import
application = app

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5000))
    # Use debug=False for production
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting WSGI app on port {port}")
    print(f"Debug mode: {debug}")
    
    app.run(debug=debug, host='0.0.0.0', port=port, threaded=True)
