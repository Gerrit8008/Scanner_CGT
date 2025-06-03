"""
Universal Scanner Route
Provides a standalone, resilient scanner implementation
"""

from flask import Blueprint, render_template, request, jsonify
import logging

# Create blueprint
universal_scanner_bp = Blueprint('universal_scanner', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@universal_scanner_bp.route('/scanner/<scanner_uid>/universal')
def universal_scanner_view(scanner_uid):
    """Serve the universal scanner page - most resilient version"""
    try:
        # Get basic scanner data
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, client_id FROM scanners WHERE scanner_id = ?', (scanner_uid,))
        scanner_row = cursor.fetchone()
        conn.close()
        
        if scanner_row:
            # Convert to dict for easier access
            if hasattr(scanner_row, 'keys'):
                scanner_data = dict(scanner_row)
            else:
                scanner_data = dict(zip(['id', 'client_id'], scanner_row))
                
            # Render the universal template
            return render_template('universal_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid,
                                client_id=scanner_data.get('client_id'))
        else:
            # Scanner not found - still render with minimal data
            logger.warning(f"Scanner not found: {scanner_uid}")
            return render_template('universal_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid)
    
    except Exception as e:
        logger.error(f"Error loading universal scanner: {e}")
        # Absolute fallback - render with minimal data
        return render_template('universal_scanner.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid)

# Alternate route to provide direct access without scanner ID
@universal_scanner_bp.route('/universal-scanner')
def direct_universal_scanner():
    """Direct access to universal scanner without requiring scanner ID"""
    return render_template('universal_scanner.html')

def register_universal_scanner(app):
    """Register the universal scanner blueprint with the Flask app"""
    app.register_blueprint(universal_scanner_bp)
    logger.info("✅ Registered universal scanner blueprint")