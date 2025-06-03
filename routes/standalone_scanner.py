"""
Standalone Scanner Route
A completely self-contained single-page scanner solution
"""

from flask import Blueprint, render_template, request, redirect, url_for
import logging

# Create blueprint
standalone_scanner_bp = Blueprint('standalone_scanner', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@standalone_scanner_bp.route('/scanner/<scanner_uid>/standalone')
def standalone_scanner_view(scanner_uid):
    """Serve the standalone scanner page"""
    try:
        # Get client_id from query params if available
        client_id = request.args.get('client_id', '')
        
        # If not in query params, try to look up in database
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
        
        # Render the standalone template
        return render_template('standalone_scanner.html', scanner_id=scanner_uid, client_id=client_id)
    
    except Exception as e:
        logger.error(f"Error loading standalone scanner: {e}")
        # Still try to render the template even if there was an error
        return render_template('standalone_scanner.html', scanner_id=scanner_uid, client_id='')

# Override the standard scanner embed route
@standalone_scanner_bp.route('/scanner/<scanner_uid>/embed')
def scanner_embed_override(scanner_uid):
    """Completely override the standard scanner embed with the standalone version"""
    # Simply redirect to the standalone version
    client_id = request.args.get('client_id', '')
    redirect_url = url_for('standalone_scanner.standalone_scanner_view', scanner_uid=scanner_uid)
    if client_id:
        redirect_url += f"?client_id={client_id}"
    return redirect(redirect_url)

def register_standalone_scanner(app):
    """Register the standalone scanner blueprint with the Flask app"""
    app.register_blueprint(standalone_scanner_bp)
    logger.info("✅ Registered standalone scanner blueprint - overriding standard scanner")