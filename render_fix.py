#!/usr/bin/env python3
"""
Fix deployment issues for Render environment
"""

import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_app_syntax():
    """Fix syntax error in app.py"""
    try:
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        
        if not os.path.exists(app_path):
            logger.error(f"app.py not found at {app_path}")
            return False
        
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Fix register_blueprint syntax error
        content = re.sub(r'app\.register_blueprint\(reports_bp\)uth_bp', 
                         'app.register_blueprint(reports_bp)\napp.register_blueprint(auth_bp)', 
                         content)
        
        # Fix import for auth_bp
        content = re.sub(r'from auth import a', 'from auth import auth_bp', content)
        
        # Remove duplicate scanner_bp imports
        scanner_imports = re.findall(r'from .*scanner_routes import scanner_bp', content)
        if len(scanner_imports) > 1:
            # Keep only the first import
            for scanner_import in scanner_imports[1:]:
                content = content.replace(scanner_import, f"# {scanner_import} (duplicate removed)")
            
            # Find the duplicate registration
            scanner_registrations = re.findall(r'app\.register_blueprint\(scanner_bp\)', content)
            if len(scanner_registrations) > 1:
                # Replace the second registration with a comment
                for i in range(1, len(scanner_registrations)):
                    content = content.replace(scanner_registrations[i], 
                                             f"# {scanner_registrations[i]} (duplicate removed)")
        
        # Write the fixed content
        with open(app_path, 'w') as f:
            f.write(content)
        
        logger.info(f"Fixed app.py syntax successfully")
        return True
    except Exception as e:
        logger.error(f"Error fixing app.py syntax: {e}")
        return False

def create_missing_imports():
    """Create stub imports for missing modules"""
    try:
        # Check if load_risk_patch.py exists
        risk_patch_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'load_risk_patch.py')
        if not os.path.exists(risk_patch_path):
            with open(risk_patch_path, 'w') as f:
                f.write("""
# Stub for load_risk_patch.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("load_risk_patch.py stub loaded")
""")
            logger.info(f"Created stub for load_risk_patch.py")
        
        # Check for other commonly imported modules and create stubs if missing
        for module_name in ['fix_auth.py', 'risk_assessment_direct_patch.py']:
            module_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), module_name)
            if not os.path.exists(module_path):
                with open(module_path, 'w') as f:
                    f.write(f"""
# Stub for {module_name}
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("{module_name} stub loaded")

# Function stubs
def authenticate_user_wrapper(username, password, ip_address=None, user_agent=None):
    # Import the real function if available
    try:
        from auth_utils import authenticate_user
        return authenticate_user(username, password, ip_address, user_agent)
    except ImportError:
        return {{"status": "error", "message": "Authentication module not available"}}

def verify_session(session_token):
    # Import the real function if available
    try:
        from auth_utils import verify_session
        return verify_session(session_token)
    except ImportError:
        return {{"status": "error", "message": "Session verification not available"}}

def logout_user(session_token):
    # Import the real function if available
    try:
        from auth_utils import logout_user
        return logout_user(session_token)
    except ImportError:
        return {{"status": "success", "message": "Logged out (stub)"}}

def create_user(username, email, password, role='client', full_name=''):
    # Import the real function if available
    try:
        from auth_utils import create_user
        return create_user(username, email, password, role, full_name)
    except ImportError:
        return {{"status": "error", "message": "User creation not available"}}

def patch_flask_routes():
    logger.info("patch_flask_routes stub called")
    return True
""")
                logger.info(f"Created stub for {module_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating missing imports: {e}")
        return False

def main():
    """Main function to fix Render deployment issues"""
    print("\n" + "=" * 80)
    print(" Render Deployment Fix")
    print("=" * 80)
    
    # Fix app.py syntax
    if fix_app_syntax():
        print("✅ Fixed app.py syntax")
    else:
        print("❌ Failed to fix app.py syntax")
    
    # Create missing imports
    if create_missing_imports():
        print("✅ Created stubs for missing imports")
    else:
        print("❌ Failed to create stubs for missing imports")
    
    print("\nRender deployment fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()