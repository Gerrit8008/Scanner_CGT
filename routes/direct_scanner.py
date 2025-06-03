"""
Direct Scanner Implementation
A simplified, ultra-reliable scanner with no external dependencies
"""

from flask import Blueprint, render_template, request, redirect, url_for
import logging

# Create blueprint
direct_scanner_bp = Blueprint('direct_scanner', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@direct_scanner_bp.route('/direct-scanner/<scanner_uid>')
def direct_scanner_view(scanner_uid):
    """Direct, simplified scanner that is guaranteed to work"""
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
                
            # Render the direct template
            return render_template('direct_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid,
                                client_id=scanner_data.get('client_id'))
        else:
            # Scanner not found - still render with minimal data
            logger.warning(f"Scanner not found: {scanner_uid}")
            return render_template('direct_scanner.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid)
    
    except Exception as e:
        logger.error(f"Error loading direct scanner: {e}")
        # Absolute fallback - render with minimal data
        return render_template('direct_scanner.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid)

# Route for scanner embed to directly use the simplified version
# This completely replaces the standard scanner with the simplified one
@direct_scanner_bp.route('/scanner/<scanner_uid>/embed')
def scanner_embed_direct(scanner_uid):
    """Replace standard scanner embed with direct version"""
    try:
        # Get client_id for tracking
        client_id = request.args.get('client_id', '')
        
        # Get basic scanner data if client_id not provided
        if not client_id:
            try:
                from client_db import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT client_id FROM scanners WHERE scanner_id = ?', (scanner_uid,))
                scanner_row = cursor.fetchone()
                conn.close()
                
                if scanner_row:
                    if hasattr(scanner_row, 'keys'):
                        client_id = scanner_row.get('client_id', '')
                    else:
                        client_id = scanner_row[0] if scanner_row[0] else ''
            except Exception as db_error:
                logger.error(f"Database error: {db_error}")
        
        # Render the direct template
        return render_template('direct_scanner.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid,
                            client_id=client_id)
        
    except Exception as e:
        logger.error(f"Error in direct scanner embed: {e}")
        # Absolute fallback
        return render_template('direct_scanner.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid)

def register_direct_scanner(app):
    """Register the direct scanner blueprint with the Flask app"""
    app.register_blueprint(direct_scanner_bp)
    logger.info("✅ Registered direct scanner blueprint")