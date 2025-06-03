"""
Scanner debug routes for troubleshooting
"""

from flask import Blueprint, render_template, request, jsonify, Response, redirect, url_for
import logging
import json
import os

# Create scanner debug blueprint
scanner_debug_bp = Blueprint('scanner_debug', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@scanner_debug_bp.route('/scanner/<scanner_uid>/debug_embed')
def scanner_debug_embed(scanner_uid):
    """Debug version of scanner embed with minimal styling and JS"""
    try:
        logger.info(f"Loading debug scanner embed for {scanner_uid}")
        
        # Get scanner data from database
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT client_id FROM scanners WHERE scanner_id = ?', (scanner_uid,))
        scanner_row = cursor.fetchone()
        conn.close()
        
        client_id = None
        if scanner_row:
            # Convert to dict for easier access
            if hasattr(scanner_row, 'keys'):
                client_id = scanner_row['client_id']
            else:
                client_id = scanner_row[0]
                
        # Create minimal branding
        client_branding = {
            'business_name': 'Debug Scanner',
            'primary_color': '#02054c',
            'secondary_color': '#35a310',
            'button_color': '#28a745'
        }
        
        # Render the simplified template
        return render_template('simple_scan.html',
                             scanner_uid=scanner_uid,
                             scanner_id=scanner_uid,
                             client_id=client_id,
                             client_branding=client_branding,
                             is_debug=True)
        
    except Exception as e:
        logger.error(f"Error in debug scanner embed: {e}")
        return f"""
        <html>
            <head><title>Scanner Debug Error</title></head>
            <body>
                <h1>Scanner Debug Error</h1>
                <p>Error loading debug scanner: {str(e)}</p>
                <p><a href="/client/scanners">Return to scanners</a></p>
            </body>
        </html>
        """

@scanner_debug_bp.route('/scanner/status')
def scanner_status():
    """Return a JSON status of all scanner-related scripts"""
    try:
        # List all scanner JS files
        js_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'js')
        scanner_js_files = [f for f in os.listdir(js_dir) if 'scanner' in f.lower() or 'scan' in f.lower()]
        
        file_info = {}
        for filename in scanner_js_files:
            filepath = os.path.join(js_dir, filename)
            if os.path.isfile(filepath):
                file_info[filename] = {
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath),
                    'path': f'/static/js/{filename}'
                }
        
        # List templates
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
        scanner_templates = [f for f in os.listdir(templates_dir) if 'scan' in f.lower()]
        
        template_info = {}
        for filename in scanner_templates:
            filepath = os.path.join(templates_dir, filename)
            if os.path.isfile(filepath):
                template_info[filename] = {
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath),
                    'path': f'/templates/{filename}'
                }
        
        return jsonify({
            'status': 'ok',
            'js_files': file_info,
            'templates': template_info,
            'request': {
                'host': request.host,
                'path': request.path,
                'user_agent': request.headers.get('User-Agent', '')
            }
        })
        
    except Exception as e:
        logger.error(f"Error in scanner status check: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@scanner_debug_bp.route('/scanner/verify_js/<filename>')
def verify_js(filename):
    """Verify that a JS file exists and return its contents"""
    try:
        js_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'js')
        file_path = os.path.join(js_dir, filename)
        
        # Security check - don't allow path traversal
        if not os.path.exists(file_path) or not os.path.isfile(file_path) or '..' in filename:
            return jsonify({
                'status': 'error',
                'message': f'File {filename} not found or invalid'
            }), 404
        
        # Get file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Return file info and content
        return jsonify({
            'status': 'ok',
            'filename': filename,
            'size': os.path.getsize(file_path),
            'modified': os.path.getmtime(file_path),
            'content': content
        })
        
    except Exception as e:
        logger.error(f"Error verifying JS file {filename}: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500