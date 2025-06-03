"""
Minimal Scanner Route
Provides an extremely lightweight scanner with no JavaScript
"""

from flask import Blueprint, render_template, request
import logging

# Create blueprint
minimal_scanner_bp = Blueprint('minimal_scanner', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@minimal_scanner_bp.route('/scanner/<scanner_uid>/minimal')
def minimal_scanner_view(scanner_uid):
    """Serve the minimal scanner page - most reliable version with no JS"""
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
                
            # Render the minimal template
            return render_template('minimal_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid,
                                client_id=scanner_data.get('client_id'))
        else:
            # Scanner not found - still render with minimal data
            logger.warning(f"Scanner not found: {scanner_uid}")
            return render_template('minimal_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid)
    
    except Exception as e:
        logger.error(f"Error loading minimal scanner: {e}")
        # Absolute fallback - render with minimal data
        return render_template('minimal_scanner.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid)

# Route for direct access
@minimal_scanner_bp.route('/minimal-scanner')
def direct_minimal_scanner():
    """Direct access to minimal scanner without requiring scanner ID"""
    scanner_id = request.args.get('scanner_id', '')
    client_id = request.args.get('client_id', '')
    return render_template('minimal_scanner.html', scanner_id=scanner_id, client_id=client_id)

def register_minimal_scanner(app):
    """Register the minimal scanner blueprint with the Flask app"""
    app.register_blueprint(minimal_scanner_bp)
    logger.info("✅ Registered minimal scanner blueprint")