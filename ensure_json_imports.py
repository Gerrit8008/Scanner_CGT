#!/usr/bin/env python3
"""
Ensure JSON imports in app.py
Makes sure app.py has all the necessary imports for JSON handling
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_app_imports():
    """Ensure app.py has all necessary imports"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    if not os.path.exists(app_path):
        logger.error(f"app.py not found at {app_path}")
        return False
    
    # Read the file
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Check if all required imports are present
    required_imports = {
        'json': 'import json',
        'jsonify': 'jsonify' in content,  # Check if it's in the line with flask imports
        'request': 'request' in content,  # Check if it's in the line with flask imports
    }
    
    # Add missing imports
    if 'import json' not in content:
        # Find the last import statement
        import_lines = content.split('\n')
        last_import_line = 0
        for i, line in enumerate(import_lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                last_import_line = i
        
        # Add import json after the last import
        import_lines.insert(last_import_line + 1, 'import json')
        content = '\n'.join(import_lines)
    
    # Make sure request is imported from flask
    if 'from flask import ' in content and 'request' not in content.split('from flask import ')[1].split('\n')[0]:
        # Find the flask import
        content = content.replace('from flask import ', 'from flask import request, ')
    
    # Make sure jsonify is imported from flask
    if 'from flask import ' in content and 'jsonify' not in content.split('from flask import ')[1].split('\n')[0]:
        # Find the flask import
        content = content.replace('from flask import ', 'from flask import jsonify, ')
    
    # Write the updated file
    with open(app_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Updated app.py with required imports")
    return True

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Ensure JSON Imports in App.py")
    print("=" * 80)
    
    # Update app.py imports
    if ensure_app_imports():
        print("✅ Added required imports to app.py")
    else:
        print("❌ Failed to update app.py imports")
    
    print("\nJSON import fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()