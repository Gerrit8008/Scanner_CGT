"""
Emergency Scanner Route
Serves a completely static HTML file for scanner functionality
"""

from flask import Flask, send_from_directory, request, redirect, url_for
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_emergency_scanner_route(app):
    """
    Apply the emergency scanner route to the Flask app
    This completely bypasses Flask templating
    """
    logger.info("Applying emergency scanner route")
    
    # Get the static folder path
    static_folder = app.static_folder
    
    @app.route('/scanner/<scanner_uid>/embed')
    def emergency_scanner_embed(scanner_uid):
        """Direct serve the static emergency scanner HTML file"""
        # Get client_id from query params if available
        client_id = request.args.get('client_id', '')
        
        # Redirect to static file with parameters
        redirect_url = f"/static/emergency_scanner.html?scanner_id={scanner_uid}"
        if client_id:
            redirect_url += f"&client_id={client_id}"
            
        return redirect(redirect_url)
    
    # Also serve directly
    @app.route('/emergency-scanner')
    def direct_emergency_scanner():
        """Serve the emergency scanner without parameters"""
        return send_from_directory(static_folder, 'emergency_scanner.html')
    
    logger.info("Emergency scanner route applied")
    
    return app

if __name__ == '__main__':
    # Test directly
    from app import app
    apply_emergency_scanner_route(app)
    print("✅ Emergency scanner route applied")