"""
Fix for blank scanner screens
Adds an automatic redirect to the minimal scanner for any blank screen issues
"""

from flask import Flask, request, redirect, url_for
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_blank_scanner_fix(app):
    """
    Apply fix to redirect any blank scanner screens to the minimal scanner
    """
    logger.info("Applying blank scanner redirect fix")
    
    # Store the original route function
    original_scanner_embed = None
    
    # Find the scanner_embed route in blueprints
    for blueprint in app.blueprints.values():
        for endpoint, view_function in blueprint.view_functions.items():
            if endpoint.endswith('scanner_embed'):
                original_scanner_embed = view_function
                break
        if original_scanner_embed:
            break
    
    if not original_scanner_embed:
        logger.warning("Could not find scanner_embed route, skipping fix")
        return
    
    # Create wrapper function to add headers
    def scanner_embed_wrapper(*args, **kwargs):
        # Get scanner_uid from kwargs
        scanner_uid = kwargs.get('scanner_uid', '')
        
        # Check if client browser reports issues
        user_agent = request.headers.get('User-Agent', '').lower()
        has_previous_issues = 'blank_screen=true' in request.url or request.args.get('blank_screen') == 'true'
        
        # Automatic redirect for known problematic browsers or reported issues
        if has_previous_issues or 'msie' in user_agent or 'trident/' in user_agent:
            logger.info(f"Redirecting scanner {scanner_uid} to minimal version (browser: {user_agent})")
            return redirect(f'/scanner/{scanner_uid}/minimal')
        
        # Process normally
        response = original_scanner_embed(*args, **kwargs)
        
        # Add headers to enable minimal scanner redirect if needed
        response.headers['X-Scanner-Minimal-URL'] = f'/scanner/{scanner_uid}/minimal'
        
        return response
    
    # Replace the original route function
    for blueprint in app.blueprints.values():
        for endpoint, view_function in blueprint.view_functions.items():
            if endpoint.endswith('scanner_embed'):
                blueprint.view_functions[endpoint] = scanner_embed_wrapper
                logger.info(f"Applied blank scanner fix to endpoint {endpoint}")
    
    logger.info("Blank scanner redirect fix applied successfully")

if __name__ == '__main__':
    # Run this file directly to apply the fix to the main app
    import sys
    sys.path.append('.')
    
    from app import app
    apply_blank_scanner_fix(app)
    
    print("✅ Blank scanner redirect fix applied")