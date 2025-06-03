"""
Client Scanner Options
Provides routes for clients to access different scanner versions
"""

from flask import Blueprint, render_template, redirect, url_for, request, flash
import logging
from functools import wraps
from client_db import get_db_connection

# Create blueprint
client_scanner_options_bp = Blueprint('client_scanner_options', __name__)

# Configure logging
logger = logging.getLogger(__name__)

# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from auth import is_logged_in
        if not is_logged_in():
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@client_scanner_options_bp.route('/client/scanner-options')
@login_required
def scanner_options():
    """Display different scanner options for a client"""
    try:
        # Get client ID from session
        from auth import get_logged_in_user
        user = get_logged_in_user()
        client_id = user.get('client_id') if user else None
        
        if not client_id:
            flash('No client account associated with this user', 'warning')
            return redirect(url_for('client.client_dashboard'))
        
        # Get scanners for this client
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scanners WHERE client_id = ?', (client_id,))
        scanners = cursor.fetchall()
        conn.close()
        
        # Convert to list of dicts
        scanner_list = []
        for scanner in scanners:
            if hasattr(scanner, 'keys'):
                scanner_dict = dict(scanner)
            else:
                # Create dict from tuple
                scanner_dict = {
                    'id': scanner[0],
                    'client_id': scanner[1],
                    'scanner_id': scanner[2],
                    'name': scanner[3],
                    'description': scanner[4]
                }
            scanner_list.append(scanner_dict)
        
        # Render scanner options page
        return render_template('client/scanner_options.html', 
                            scanners=scanner_list,
                            client_id=client_id)
        
    except Exception as e:
        logger.error(f"Error displaying scanner options: {e}")
        flash('Error loading scanner options', 'danger')
        return redirect(url_for('client.client_dashboard'))

def register_client_scanner_options(app):
    """Register the client scanner options blueprint with the Flask app"""
    app.register_blueprint(client_scanner_options_bp)
    logger.info("✅ Registered client scanner options blueprint")