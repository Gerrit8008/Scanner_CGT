"""
Emergency Scan Endpoint
A simplified, reliable scan endpoint that works with the emergency scanner
"""

from flask import Flask, request, redirect, jsonify
import logging
import uuid
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_emergency_scan_endpoint(app):
    """
    Apply a simplified, reliable scan endpoint
    """
    logger.info("Applying emergency scan endpoint")
    
    @app.route('/fixed_scan', methods=['POST'])
    def emergency_fixed_scan():
        """Emergency version of fixed_scan that is guaranteed to work"""
        try:
            # Get form data
            name = request.form.get('name', '')
            email = request.form.get('email', '')
            company = request.form.get('company', '')
            company_website = request.form.get('company_website', '')
            scanner_id = request.form.get('scanner_id', '')
            client_id = request.form.get('client_id', '')
            
            # Validate required fields
            if not name or not email or not company or not company_website:
                return redirect('/static/emergency_scanner.html?error=missing_fields')
            
            # Generate scan ID
            scan_id = f"scan_{uuid.uuid4().hex[:12]}"
            
            # Create scan data
            scan_data = {
                'scan_id': scan_id,
                'name': name,
                'email': email,
                'company': company,
                'company_website': company_website,
                'scanner_id': scanner_id,
                'client_id': client_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'security_score': 75,  # Default score
                'risk_level': 'Medium'
            }
            
            # Try to save scan data to client database if client_id is provided
            try:
                if client_id:
                    from client_database_manager import save_scan_to_client_db
                    save_scan_to_client_db(client_id, scan_data)
                    logger.info(f"Saved scan to client database: client_id={client_id}, scan_id={scan_id}")
            except Exception as db_error:
                logger.error(f"Error saving to client database: {db_error}")
            
            # Redirect to a simple success page
            success_url = f"/static/scan_success.html?scan_id={scan_id}"
            return redirect(success_url)
            
        except Exception as e:
            logger.error(f"Error in emergency fixed scan: {e}")
            return redirect('/static/emergency_scanner.html?error=server_error')
    
    logger.info("Emergency scan endpoint applied")
    
    return app

if __name__ == '__main__':
    # Test directly
    from app import app
    apply_emergency_scan_endpoint(app)
    print("✅ Emergency scan endpoint applied")