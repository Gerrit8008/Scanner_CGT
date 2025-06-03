#!/usr/bin/env python3
"""
Fix Scanner Routes for JSON Parsing Issues
This script modifies the scanner routes to ensure proper JSON responses
"""

import os
import json
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_scanner_routes():
    """Fix the scanner_routes.py file to ensure proper JSON parsing"""
    # Check both potential locations
    scanner_routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'scanner_routes.py')
    if not os.path.exists(scanner_routes_path):
        scanner_routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scanner_routes.py')
        if not os.path.exists(scanner_routes_path):
            logger.error("Cannot find scanner_routes.py in either routes/ or root directory")
            return False
    
    logger.info(f"Fixing scanner routes in {scanner_routes_path}")
    
    # Read the file
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # First, ensure we're properly adding CORS headers to all responses
    content = ensure_cors_headers(content)
    
    # Second, fix any JSON parsing in the routes
    content = fix_json_parsing(content)
    
    # Write the fixed file
    with open(scanner_routes_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Scanner routes fixed successfully")
    return True

def ensure_cors_headers(content):
    """Ensure that all routes properly handle CORS headers"""
    # Find all route definitions
    route_pattern = r'@scanner_bp\.route\([\'"](.+?)[\'"](.*?)\)\s*def\s+(\w+)'
    
    # Extract routes
    routes = re.findall(route_pattern, content, re.DOTALL)
    
    for route, options, function_name in routes:
        # Check if this is an API route
        if 'api' in route.lower() and 'methods=' in options:
            # Check if OPTIONS is already in methods
            if 'OPTIONS' not in options:
                # Add OPTIONS to methods list
                methods_pattern = r'methods=\[(.*?)\]'
                methods_match = re.search(methods_pattern, options)
                
                if methods_match:
                    methods = methods_match.group(1)
                    if 'OPTIONS' not in methods:
                        new_methods = methods + ", 'OPTIONS'"
                        new_options = options.replace(methods, new_methods)
                        content = content.replace(f"@scanner_bp.route('{route}'{options})", 
                                                f"@scanner_bp.route('{route}'{new_options})")
            
            # Check if the function handles OPTIONS requests
            function_pattern = f"def\\s+{function_name}\\s*\\(.*?\\)\\s*:.*?if\\s+request\\.method\\s+==\\s+['\"]OPTIONS['\"]"
            if not re.search(function_pattern, content, re.DOTALL):
                # Function doesn't handle OPTIONS, so add the handler
                function_def_pattern = f"def\\s+{function_name}\\s*\\(.*?\\)\\s*:"
                function_def_match = re.search(function_def_pattern, content)
                
                if function_def_match:
                    function_start = function_def_match.end()
                    indent = get_indent_at_position(content, function_start)
                    
                    # Insert OPTIONS handling code
                    cors_handler = f"\n{indent}# Handle CORS preflight request\n"
                    cors_handler += f"{indent}if request.method == 'OPTIONS':\n"
                    cors_handler += f"{indent}    response = jsonify({{'status': 'ok'}})\n"
                    cors_handler += f"{indent}    response.headers['Access-Control-Allow-Origin'] = '*'\n"
                    cors_handler += f"{indent}    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'\n"
                    cors_handler += f"{indent}    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'\n"
                    cors_handler += f"{indent}    return response\n"
                    
                    # Insert after function definition and docstring if present
                    docstring_end = find_docstring_end(content, function_start)
                    insert_pos = docstring_end if docstring_end > function_start else function_start
                    
                    content = content[:insert_pos] + cors_handler + content[insert_pos:]
    
    return content

def fix_json_parsing(content):
    """Fix JSON parsing in scanner routes"""
    # Look for patterns where request.get_json() is called without error handling
    json_pattern = r'(request\.get_json\(\))'
    
    # Replace with safe version that includes error handling
    safe_json_code = '''try:
            if request.is_json:
                scan_data = request.get_json()
            else:
                # Try to parse body as JSON anyway or get form data
                try:
                    if request.content_type and 'form' in request.content_type:
                        scan_data = {k: v for k, v in request.form.items()}
                    else:
                        # Try to parse as JSON
                        scan_data = json.loads(request.data.decode('utf-8')) if request.data else {}
                except Exception as parse_error:
                    logging.error(f"Error parsing request data: {parse_error}")
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid request format. Expected JSON or form data.'
                    }), 400
        except Exception as e:
            logging.error(f"Error handling request data: {e}")
            return jsonify({'status': 'error', 'message': 'Unable to process request data'}), 400
            
            # Original code continues here
            scan_data'''
    
    # Find matches and replace
    matches = re.findall(json_pattern, content)
    if matches:
        logger.info(f"Found {len(matches)} instances of request.get_json() without error handling")
        
        for match in matches:
            # Get the indentation level
            idx = content.find(match)
            if idx > 0:
                line_start = content.rfind('\n', 0, idx) + 1
                indent = content[line_start:idx]
                
                # Format the replacement code with the correct indentation
                replacement = safe_json_code.replace('\n', f'\n{indent}')
                
                # Replace in content
                content = content.replace(match, replacement, 1)
    
    # Ensure all API responses include CORS headers
    api_response_pattern = r'return\s+jsonify\('
    api_response_matches = re.findall(api_response_pattern, content)
    
    if api_response_matches:
        logger.info(f"Found {len(api_response_matches)} API responses to enhance with CORS headers")
        
        # Replace with version that adds CORS headers
        for match in api_response_matches:
            idx = content.find(match)
            if idx > 0:
                line_start = content.rfind('\n', 0, idx) + 1
                indent = content[line_start:idx]
                
                # Get end of the jsonify statement
                end_idx = find_closing_parenthesis(content, idx + len(match))
                if end_idx > idx:
                    jsonify_call = content[idx:end_idx+1]
                    
                    # Create replacement with CORS headers
                    replacement = f"""response = {jsonify_call}
{indent}
{indent}# Add CORS headers
{indent}response.headers['Access-Control-Allow-Origin'] = '*'
{indent}response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
{indent}response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
{indent}
{indent}return response"""
                    
                    # Replace in content
                    content = content.replace(jsonify_call, replacement, 1)
    
    return content

def find_closing_parenthesis(text, start_pos):
    """Find the position of the closing parenthesis matching the opening one"""
    stack = []
    for i in range(start_pos, len(text)):
        if text[i] == '(':
            stack.append('(')
        elif text[i] == ')':
            if stack:
                stack.pop()
            else:
                return i  # This is an error condition, but we'll ignore it
            if not stack:
                return i
    return -1

def get_indent_at_position(content, pos):
    """Get the indentation at the given position in the content"""
    line_start = content.rfind('\n', 0, pos) + 1
    non_space = pos
    for i in range(line_start, len(content)):
        if i >= len(content) or not content[i].isspace():
            non_space = i
            break
    return content[line_start:non_space]

def find_docstring_end(content, start_pos):
    """Find the end position of a docstring if present after start_pos"""
    # Check for docstring pattern
    docstring_pattern = r'"""(.*?)"""'
    docstring_match = re.search(docstring_pattern, content[start_pos:], re.DOTALL)
    
    if docstring_match:
        return start_pos + docstring_match.end()
    
    return start_pos

def fix_app_json_error_handler():
    """Fix the app.py JSON error handler"""
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
    
    if not os.path.exists(app_path):
        logger.error(f"app.py not found at {app_path}")
        return False
    
    with open(app_path, 'r') as f:
        content = f.read()
    
    # Look for the 400 error handler
    error_handler_pattern = r'@app\.errorhandler\(400\)(.*?)def\s+bad_request.*?\)'
    error_handler_match = re.search(error_handler_pattern, content, re.DOTALL)
    
    if error_handler_match:
        # The 400 error handler exists, check if it handles JSON parsing errors
        handler_code = error_handler_match.group(0)
        
        if 'Invalid JSON format' not in handler_code:
            # Add JSON error handling
            json_handler = """@app.errorhandler(400)
def bad_request(e):
    """"Handle bad request errors, including JSON parse errors"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    accept_header = request.headers.get('Accept', '')
    wants_json = 'application/json' in accept_header
    
    # Check for JSON parsing error
    is_json_error = isinstance(e, Exception) and hasattr(e, 'description') and \\
                   ('Failed to decode JSON object' in str(e.description) or 'Not a JSON' in str(e.description))
    
    if is_ajax or wants_json or is_json_error:
        # Return JSON error for AJAX requests or JSON errors
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format in request' if is_json_error else str(e.description) if hasattr(e, 'description') else 'Bad request'
        }), 400
    else:
        # Return HTML for regular requests
        return render_template('error.html', error=e, title="Bad Request", message="The request could not be understood by the server."), 400"""
            
            # Replace old handler with new one
            content = re.sub(error_handler_pattern, json_handler, content, flags=re.DOTALL)
        else:
            logger.info("400 error handler already has JSON parsing error handling")
    else:
        # Add the 400 error handler
        # Find where to add it (after another error handler)
        error_handlers_pattern = r'# Error handlers'
        error_handlers_match = re.search(error_handlers_pattern, content)
        
        if error_handlers_match:
            insert_pos = error_handlers_match.end()
            
            # Add the new handler
            json_handler = """

@app.errorhandler(400)
def bad_request(e):
    """"Handle bad request errors, including JSON parse errors"""
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    accept_header = request.headers.get('Accept', '')
    wants_json = 'application/json' in accept_header
    
    # Check for JSON parsing error
    is_json_error = isinstance(e, Exception) and hasattr(e, 'description') and \\
                   ('Failed to decode JSON object' in str(e.description) or 'Not a JSON' in str(e.description))
    
    if is_ajax or wants_json or is_json_error:
        # Return JSON error for AJAX requests or JSON errors
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON format in request' if is_json_error else str(e.description) if hasattr(e, 'description') else 'Bad request'
        }), 400
    else:
        # Return HTML for regular requests
        return render_template('error.html', error=e, title="Bad Request", message="The request could not be understood by the server."), 400
"""
            
            content = content[:insert_pos] + json_handler + content[insert_pos:]
        else:
            logger.warning("Could not find where to add error handler in app.py")
            return False
    
    # Write the updated content
    with open(app_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Updated app.py with enhanced JSON error handling")
    return True

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Scanner Routes JSON Parsing Fix")
    print("=" * 80)
    
    # Fix scanner routes
    if fix_scanner_routes():
        print("✅ Scanner routes fixed successfully")
    else:
        print("❌ Failed to fix scanner routes")
    
    # Fix app.py JSON error handler
    if fix_app_json_error_handler():
        print("✅ App.py JSON error handler fixed")
    else:
        print("❌ Failed to fix app.py JSON error handler")
    
    print("\nJSON parsing fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()