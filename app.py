"""
CybrScan - Security Scanner Platform
"""
# Import risk assessment color patch
import load_risk_patch
from routes.scanner_routes import scanner_bp
from reports_routes import reports_bp

from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session, g, abort
import os
import sys
import logging
import sqlite3
from datetime import datetime, timedelta
import uuid
import json
import secrets
from werkzeug.utils import secure_filename
from functools import wraps

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object('config.Config')

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# Register Blueprints
from auth import auth_bp
app.register_blueprint(reports_bp)
app.register_blueprint(auth_bp)

from client import client_bp
app.register_blueprint(client_bp)

from admin import admin_bp
app.register_blueprint(admin_bp)

# Scanner blueprint is already imported at the top
app.register_blueprint(scanner_bp)

# Import scanner debug routes
try:
    from routes.scanner_debug import scanner_debug_bp
    app.register_blueprint(scanner_debug_bp)
    logger.info("Registered scanner debug routes")
except ImportError as e:
    logger.warning(f"Could not import scanner debug routes: {e}")

# Import scan endpoint fix
try:
    from routes.scan_endpoint_fix import register_scan_endpoint_fix
    register_scan_endpoint_fix(app)
    logger.info("Registered scan endpoint fix")
except ImportError as e:
    logger.warning(f"Could not import scan endpoint fix: {e}")

# Import universal scanner
try:
    from routes.universal_scanner import register_universal_scanner
    register_universal_scanner(app)
    logger.info("✅ Registered universal scanner blueprint")
except ImportError as e:
    logger.warning(f"Could not import universal scanner: {e}")

# Import fixed scan routes
try:
    from fixed_scan_routes import fixed_scan_bp
    app.register_blueprint(fixed_scan_bp)
    logger.info("Registered fixed scan routes")
except ImportError as e:
    logger.warning(f"Could not import fixed scan routes: {e}")

# Import API routes
try:
    from api import api_bp
    app.register_blueprint(api_bp)
except ImportError:
    logger.warning("API blueprint not found")

# Default route
@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

# Error handlers
@app.errorhandler(404)

@app.errorhandler(400)
def bad_request(e):
    """Handle bad request errors, including JSON parse errors"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    accept_header = request.headers.get('Accept', '')
    wants_json = 'application/json' in accept_header
    
    # Check for JSON parsing error
    is_json_error = isinstance(e, Exception) and hasattr(e, 'description') and \
                   ('Failed to decode JSON object' in str(e.description) or 'Not a JSON' in str(e.description))
    
    if is_ajax or wants_json or is_json_error:
        # Return JSON error for AJAX requests or JSON errors
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format in request' if is_json_error else str(e.description) if hasattr(e, 'description') else 'Bad request'
        }), 400
    else:
        # Return HTML for regular requests
        return render_template('error.html', error=e, title="Bad Request", message="The request could not be understood by the server."), 400

def page_not_found(e):
    return render_template('error.html', error=e, title="Page Not Found", message="The page you're looking for doesn't exist."), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error=e, title="Internal Server Error", message="Something went wrong on our end."), 500

# Apply any patches
try:
    from risk_assessment_direct_patch import patch_flask_routes
    patch_flask_routes()
    logger.info("Applied risk assessment patch to Flask routes")
except Exception as e:
    logger.warning(f"Failed to apply risk assessment patch: {e}")

if __name__ == "__main__":
    # For development
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
    
    # Note: For production, use gunicorn with increased timeout:
    # gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 app:app