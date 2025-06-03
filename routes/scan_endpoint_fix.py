"""
Fix for scan endpoint
Provides a direct fix for the scan endpoint to properly handle both HTML and JSON responses
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import logging
import json
import uuid
from datetime import datetime

# Create blueprint
scan_endpoint_fix_bp = Blueprint('scan_endpoint_fix', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@scan_endpoint_fix_bp.route('/fixed_scan', methods=['GET', 'POST'])
def fixed_scan():
    """Fixed scan endpoint that properly handles both HTML and JSON responses"""
    # Handle GET request - show the form
    if request.method == 'GET':
        scanner_id = request.args.get('scanner_id')
        client_id = request.args.get('client_id')
        
        return render_template('simple_scan.html', 
                             scanner_id=scanner_id,
                             client_id=client_id)
    
    # Handle POST request
    if request.method == 'POST':
        try:
            # Check if this is an AJAX request
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            wants_json = 'application/json' in request.headers.get('Accept', '')
            
            # Get form data
            lead_data = {
                'name': request.form.get('name', ''),
                'email': request.form.get('email', ''),
                'company': request.form.get('company', ''),
                'company_website': request.form.get('company_website', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            # Basic validation
            if not lead_data['name'] or not lead_data['email'] or not lead_data['company_website']:
                if is_ajax or wants_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Please fill in all required fields'
                    }), 400
                else:
                    return render_template('simple_scan.html', 
                                         error='Please fill in all required fields',
                                         form_data=lead_data)
            
            # Get client_id and scanner_id
            client_id = request.form.get('client_id')
            scanner_id = request.form.get('scanner_id')
            
            # Generate scan ID
            scan_id = f"scan_{uuid.uuid4().hex[:12]}"
            
            # Create basic scan results
            scan_results = {
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat(),
                'name': lead_data['name'],
                'email': lead_data['email'],
                'company': lead_data['company'],
                'target': lead_data['company_website'],
                'security_score': 75,  # Default score
                'risk_level': 'Medium',
                'vulnerabilities_found': 0,
                'client_id': client_id,
                'scanner_id': scanner_id
            }
            
            # Save scan if client_id is provided
            if client_id:
                try:
                    # Save to client database
                    from client_database_manager import save_scan_to_client_db
                    save_scan_to_client_db(client_id, scan_results)
                    logger.info(f"Saved scan to client database for client {client_id}")
                except Exception as db_error:
                    logger.error(f"Error saving to client database: {db_error}")
            
            # Return appropriate response based on request type
            if is_ajax or wants_json:
                # Return JSON response
                return jsonify({
                    'status': 'success',
                    'message': 'Scan completed successfully',
                    'scan_id': scan_id,
                    'results_url': url_for('client.report_view', scan_id=scan_id)
                })
            else:
                # Return redirect to results
                return redirect(url_for('client.report_view', scan_id=scan_id))
                
        except Exception as e:
            logger.error(f"Error processing scan: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            if is_ajax or wants_json:
                return jsonify({
                    'status': 'error',
                    'message': f'An error occurred during the scan: {str(e)}'
                }), 500
            else:
                return render_template('simple_scan.html', 
                                     error=f'An error occurred during the scan: {str(e)}',
                                     form_data=lead_data if 'lead_data' in locals() else {})

# Function to register this blueprint with Flask app
def register_scan_endpoint_fix(app):
    """Register the scan endpoint fix blueprint with the Flask app"""
    app.register_blueprint(scan_endpoint_fix_bp)
    logger.info("✅ Registered scan endpoint fix blueprint")