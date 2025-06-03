#!/usr/bin/env python3
"""
Fix JSON parsing issues in the scan process
"""

import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_scanner_js():
    """Fix JSON parsing in scanner.js"""
    try:
        scanner_js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/js/scanner.js')
        
        if not os.path.exists(scanner_js_path):
            logger.error(f"scanner.js not found at {scanner_js_path}")
            return False
            
        with open(scanner_js_path, 'r') as f:
            content = f.read()
            
        # Add error handling for JSON parsing
        if 'return await response.json();' in content:
            # Replace direct JSON parsing with error handling
            new_content = content.replace(
                'return await response.json();',
                '''const text = await response.text();
            try {
                return JSON.parse(text);
            } catch (e) {
                console.error('Error parsing JSON response:', e);
                console.error('Raw response:', text);
                return { 
                    success: false, 
                    error: 'Invalid server response format. Please try again or contact support.' 
                };
            }'''
            )
            
            # Write the updated file
            with open(scanner_js_path, 'w') as f:
                f.write(new_content)
                
            logger.info(f"Updated scanner.js with improved JSON parsing")
            return True
        else:
            logger.warning("Could not find JSON parsing code in scanner.js")
            return False
            
    except Exception as e:
        logger.error(f"Error fixing scanner.js: {e}")
        return False

def fix_scanner_script_js():
    """Fix JSON parsing in scanner_script.js"""
    try:
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/js/scanner_script.js')
        
        if not os.path.exists(script_path):
            logger.warning(f"scanner_script.js not found at {script_path}")
            return False
            
        with open(script_path, 'r') as f:
            content = f.read()
            
        # Check if there's any fetch/XHR code that needs error handling
        if 'fetch(' in content and '.then(' in content:
            # Add better error handling to any fetch calls
            fetch_pattern = r'fetch\((.*?)\)\s*\.then\((.*?)\.json\(\)\)'
            
            # Replace with improved error handling
            improved_fetch = r'fetch(\1).then(response => {' + \
                r'\n                if (!response.ok) { throw new Error(`HTTP error ${response.status}`); }' + \
                r'\n                return response.text().then(text => {' + \
                r'\n                    try {' + \
                r'\n                        return JSON.parse(text);' + \
                r'\n                    } catch (e) {' + \
                r'\n                        console.error("JSON parse error:", e, "Raw text:", text);' + \
                r'\n                        throw new Error("Invalid response format");' + \
                r'\n                    }' + \
                r'\n                });' + \
                r'\n            })'
                
            new_content = re.sub(fetch_pattern, improved_fetch, content)
            
            # Write the updated file
            with open(script_path, 'w') as f:
                f.write(new_content)
                
            logger.info(f"Updated scanner_script.js with improved JSON parsing")
            return True
        else:
            logger.info("No fetch calls found in scanner_script.js that need updating")
            return True
            
    except Exception as e:
        logger.error(f"Error fixing scanner_script.js: {e}")
        return False

def fix_scan_endpoint():
    """Fix the scan endpoint to always return valid JSON"""
    try:
        routes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes')
        
        # Look for scan route files in both locations
        scan_routes_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scanner_routes.py'),
            os.path.join(routes_dir, 'scanner_routes.py')
        ]
        
        fixed = False
        
        for path in scan_routes_paths:
            if os.path.exists(path):
                logger.info(f"Found scanner routes at {path}")
                
                with open(path, 'r') as f:
                    content = f.read()
                
                # Find route functions that handle scan requests
                scan_routes = re.findall(r'@\w+_bp\.route\([\'"].*?scan.*?[\'"].*?\)\s*def\s+(\w+)', content)
                
                if scan_routes:
                    logger.info(f"Found scan route functions: {scan_routes}")
                    
                    # Add content type validation and error handling
                    for route_func in scan_routes:
                        # Find the function definition
                        func_pattern = rf'def\s+{route_func}\s*\([^)]*\):\s*.*?\"\"\"\s*(.*?)\s*return\s'
                        func_match = re.search(func_pattern, content, re.DOTALL)
                        
                        if func_match:
                            func_body = func_match.group(1)
                            
                            # Check if the function already has error handling
                            if 'try:' in func_body and 'except' in func_body:
                                logger.info(f"Function {route_func} already has error handling")
                                continue
                                
                            # Add error handling to the function
                            new_func_body = f"""    try:
        # Ensure request is properly formatted
        if request.is_json:
            scan_data = request.get_json()
        else:
            # Handle form data or invalid content type
            try:
                if request.content_type and 'form' in request.content_type:
                    scan_data = {{k: v for k, v in request.form.items()}}
                else:
                    # Try to parse body as JSON anyway
                    scan_data = json.loads(request.data.decode('utf-8')) if request.data else {{}}
            except Exception as parse_error:
                logging.error(f"Error parsing request data: {{parse_error}}")
                return jsonify({{
                    'status': 'error',
                    'message': 'Invalid request format. Expected JSON or form data.'
                }}), 400
                
{func_body}
    except Exception as e:
        logging.error(f"Error processing scan request: {{e}}")
        import traceback
        logging.error(traceback.format_exc())
        return jsonify({{
            'status': 'error',
            'message': f'Server error: {{str(e)}}'
        }}), 500"""
                            
                            # Replace function body with new one
                            content = content.replace(func_match.group(1), new_func_body)
                            fixed = True
                    
                    # Write updated content
                    if fixed:
                        with open(path, 'w') as f:
                            f.write(content)
                        
                        logger.info(f"Updated scan routes in {path} with improved error handling")
                else:
                    logger.warning(f"No scan route functions found in {path}")
            
        return fixed
    except Exception as e:
        logger.error(f"Error fixing scan endpoint: {e}")
        return False

def create_error_handler():
    """Add a global error handler for JSON parsing errors"""
    try:
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        
        if not os.path.exists(app_path):
            logger.error(f"app.py not found at {app_path}")
            return False
            
        with open(app_path, 'r') as f:
            content = f.read()
            
        # Check if error handler already exists
        if '@app.errorhandler(400)' in content:
            logger.info("400 error handler already exists in app.py")
            return True
            
        # Find the last error handler
        last_error_handler = re.search(r'@app\.errorhandler\(\d+\)[^@]*?$', content, re.MULTILINE | re.DOTALL)
        
        if last_error_handler:
            # Add new error handler after the last one
            json_error_handler = """

@app.errorhandler(400)
def bad_request(e):
    \"\"\"Handle bad request errors, including JSON parse errors\"\"\"
    if isinstance(e, Exception) and hasattr(e, 'description') and 'Failed to decode JSON object' in str(e.description):
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format in request'
        }), 400
    return render_template('error.html', error=e, title="Bad Request", message="The request could not be understood by the server."), 400
"""
            
            # Insert the new error handler
            insert_pos = last_error_handler.end()
            new_content = content[:insert_pos] + json_error_handler + content[insert_pos:]
            
            with open(app_path, 'w') as f:
                f.write(new_content)
                
            logger.info("Added JSON error handler to app.py")
            return True
        else:
            logger.warning("Could not find existing error handlers in app.py")
            return False
            
    except Exception as e:
        logger.error(f"Error creating error handler: {e}")
        return False

def main():
    """Main function to fix JSON parsing issues"""
    print("\n" + "=" * 80)
    print(" JSON Parsing Fix")
    print("=" * 80)
    
    # Fix scanner.js
    if fix_scanner_js():
        print("✅ Updated scanner.js with improved JSON parsing")
    else:
        print("❌ Failed to update scanner.js")
        
    # Fix scanner_script.js
    if fix_scanner_script_js():
        print("✅ Updated scanner_script.js with improved JSON parsing")
    else:
        print("❌ Failed to update scanner_script.js")
        
    # Fix scan endpoint
    if fix_scan_endpoint():
        print("✅ Updated scan endpoints with improved error handling")
    else:
        print("❌ Failed to update scan endpoints")
        
    # Add error handler
    if create_error_handler():
        print("✅ Added global JSON error handler")
    else:
        print("❌ Failed to add global JSON error handler")
    
    print("\nJSON parsing fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()