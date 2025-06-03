#!/usr/bin/env python3
"""
Comprehensive JSON Parsing Fix Script
This script fixes all potential issues related to JSON parsing
"""

import os
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_scan_routes():
    """Add CORS headers and proper error handling to scan routes"""
    scan_routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'scan_routes.py')
    
    if not os.path.exists(scan_routes_path):
        logger.warning(f"scan_routes.py not found at {scan_routes_path}")
        return False
    
    # Read the file
    with open(scan_routes_path, 'r') as f:
        content = f.read()
    
    # Find API endpoints
    api_pattern = r'@scan_bp\.route\([\'\"]/api/.*?methods=\[.*?\]\)'
    api_routes = re.findall(api_pattern, content, re.DOTALL)
    
    # Add OPTIONS to methods and CORS headers
    for api_route in api_routes:
        # Add OPTIONS to methods if not present
        if "'OPTIONS'" not in api_route and '"OPTIONS"' not in api_route:
            # Add OPTIONS to methods list
            modified_route = api_route.replace("methods=[", "methods=['OPTIONS', ")
            content = content.replace(api_route, modified_route)
    
    # Find POST requests
    post_handlers = re.finditer(r'@scan_bp\.route\([\'\"](.*?)[\'\"], methods=\[.*?\'POST\'.*?\]\)\s*def\s+(\w+)', content)
    
    for match in post_handlers:
        route = match.group(1)
        function_name = match.group(2)
        
        # Get function body
        function_pattern = f"def\\s+{function_name}\\s*\\([^)]*\\):(.*?)(?=@|$)"
        function_match = re.search(function_pattern, content, re.DOTALL)
        
        if function_match:
            function_body = function_match.group(1)
            
            # Check if it already handles OPTIONS
            if "request.method == 'OPTIONS'" not in function_body:
                # Add OPTIONS handling
                # Find the right position (after docstring)
                docstring_match = re.search(r'def\s+' + function_name + r'\s*\([^)]*\):\s*""".*?"""', content, re.DOTALL)
                
                if docstring_match:
                    insert_pos = docstring_match.end()
                else:
                    # No docstring, find position after function def
                    fn_def_match = re.search(r'def\s+' + function_name + r'\s*\([^)]*\):', content)
                    if fn_def_match:
                        insert_pos = fn_def_match.end()
                    else:
                        continue
                
                # Get indentation
                next_line_pos = content.find('\n', insert_pos) + 1
                next_line_end = content.find('\n', next_line_pos)
                if next_line_end > next_line_pos:
                    whitespace = re.match(r'^(\s+)', content[next_line_pos:next_line_end])
                    if whitespace:
                        indent = whitespace.group(1)
                    else:
                        indent = '    '
                else:
                    indent = '    '
                
                # CORS handling code
                cors_code = f"\n{indent}# Handle CORS preflight request\n"
                cors_code += f"{indent}if request.method == 'OPTIONS':\n"
                cors_code += f"{indent}    response = jsonify({{'status': 'ok'}})\n"
                cors_code += f"{indent}    response.headers['Access-Control-Allow-Origin'] = '*'\n"
                cors_code += f"{indent}    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'\n"
                cors_code += f"{indent}    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'\n"
                cors_code += f"{indent}    return response\n"
                
                # Insert CORS code
                content = content[:insert_pos] + cors_code + content[insert_pos:]
    
    # Make sure we have proper JSON parsing error handling
    if "Invalid JSON format" not in content:
        # Find all places with request.get_json()
        json_pattern = r'([^_]request\.get_json\(\))'
        
        # Replace with safe version
        safe_json = '''try:
            if request.is_json:
                data = request.get_json()
            else:
                # Try to parse body as JSON anyway or get form data
                try:
                    if request.content_type and 'form' in request.content_type:
                        data = {k: v for k, v in request.form.items()}
                    else:
                        # Try to parse as JSON
                        data = json.loads(request.data.decode('utf-8')) if request.data else {}
                except Exception as parse_error:
                    logging.error(f"Error parsing request data: {parse_error}")
                    # Check if this is an AJAX request
                    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                    if is_ajax:
                        return jsonify({
                            'status': 'error',
                            'message': 'Invalid request format. Expected JSON or form data.'
                        }), 400
                    else:
                        return render_template('error.html', 
                                             error="Invalid request format", 
                                             message="The request could not be processed. Please try again.")
        except Exception as e:
            logging.error(f"Error handling request data: {e}")
            return jsonify({'status': 'error', 'message': 'Unable to process request data'}), 400
            
            # Continue with data instead of request.get_json()
            data'''
        
        # Find matches and replace
        content_new = re.sub(json_pattern, lambda m: m.group(0).replace('request.get_json()', safe_json), content)
        
        if content_new != content:
            content = content_new
            logger.info("Added safe JSON parsing to scan_routes.py")
    
    # Write the updated file
    with open(scan_routes_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Fixed scan routes with CORS headers and JSON error handling")
    return True

def update_scan_form():
    """Update scan.html form to handle JSON parsing errors"""
    scan_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'scan.html')
    
    if not os.path.exists(scan_html_path):
        logger.warning(f"scan.html not found at {scan_html_path}")
        return False
    
    # Read the file
    with open(scan_html_path, 'r') as f:
        content = f.read()
    
    # Check if we need to fix the fetch call
    fetch_pattern = r'fetch\([\'\"]/scan[\'\"](.*?)\.then\(response\s*=>\s*\{.*?response\.json\(\)'
    
    if re.search(fetch_pattern, content, re.DOTALL):
        # Find the fetch call and modify it
        form_submission_pattern = r'(function\s+setupFormSubmission\(\)\s*\{.*?\}\s*\})'
        
        form_submission_match = re.search(form_submission_pattern, content, re.DOTALL)
        if form_submission_match:
            old_submission = form_submission_match.group(1)
            
            # Add updated form submission
            new_submission = """function setupFormSubmission() {
            const scanForm = document.getElementById('scanForm');
            const scanProgress = document.getElementById('scanProgress');
            const scanComplete = document.getElementById('scanComplete');
            
            scanForm.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Check terms consent
                if (!document.getElementById('terms-consent').checked) {
                    alert('Please accept the terms to proceed with the scan.');
                    return;
                }
                
                // Hide form, show progress
                this.style.display = 'none';
                scanProgress.style.display = 'block';
                
                // Scroll to top of progress
                scanProgress.scrollIntoView({ behavior: 'smooth' });
                
                // Simulate scan progress
                simulateScanProgress();
                
                // After progress animation completes, submit the form to server
                setTimeout(() => {
                    // Create FormData from the form
                    const formData = new FormData(this);
                    
                    // Add client info
                    formData.append('client_os', navigator.platform || 'Unknown');
                    formData.append('client_browser', navigator.userAgent || 'Unknown');
                    
                    // Set headers to indicate this is an AJAX request
                    const headers = {
                        'X-Requested-With': 'XMLHttpRequest',
                        'Accept': 'application/json'
                    };
                    
                    // Submit the form to the server
                    fetch('/scan', {
                        method: 'POST',
                        headers: headers,
                        body: formData
                    })
                    .then(response => {
                        // Handle server response
                        scanProgress.style.display = 'none';
                        
                        // First check if response is a redirect
                        if (response.redirected) {
                            // Server is redirecting us - follow the redirect
                            window.location.href = response.url;
                            return null; // End execution here
                        }
                        
                        // Now get the response text regardless of content type
                        return response.text().then(text => {
                            // First check if it's a redirect URL in text
                            if (text.includes('/results?scan_id=') || text.includes('/client/report')) {
                                // Try to extract the URL
                                const redirectMatch = text.match(/\\/results\\?scan_id=([a-zA-Z0-9_]+)/);
                                const reportMatch = text.match(/\\/client\\/report\\/([a-zA-Z0-9_]+)/);
                                
                                if (redirectMatch && redirectMatch[0]) {
                                    window.location.href = redirectMatch[0];
                                    return null;
                                } else if (reportMatch && reportMatch[0]) {
                                    window.location.href = reportMatch[0];
                                    return null;
                                }
                            }
                            
                            // Check if it's likely HTML
                            if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
                                console.log('Server returned HTML instead of JSON');
                                // For HTML responses, check for successful redirect
                                if (response.status === 200 && text.includes('Scan Results') && text.includes('security')) {
                                    // This is likely a successful scan that returned HTML - show completion
                                    scanComplete.style.display = 'block';
                                    // Extract scan ID if possible
                                    const scanIdMatch = text.match(/scan_id=([a-zA-Z0-9_]+)/) || text.match(/scan\\/([a-zA-Z0-9_]+)/);
                                    if (scanIdMatch && scanIdMatch[1]) {
                                        const viewResultsBtn = document.querySelector('#scanComplete a.btn');
                                        viewResultsBtn.href = `/results?scan_id=${scanIdMatch[1]}`;
                                    }
                                    return null;
                                } else if (text.includes('Error:') || text.includes('error') || response.status >= 400) {
                                    // Try to extract error message from HTML
                                    let errorMsg = 'Server error occurred';
                                    const errorMatch = text.match(/<div class=\"alert alert-danger\">([^<]+)<\\/div>/) || 
                                                       text.match(/Error: ([^<]+)/);
                                    if (errorMatch && errorMatch[1]) {
                                        errorMsg = errorMatch[1].trim();
                                    }
                                    throw new Error(errorMsg);
                                } else {
                                    // Unknown HTML response
                                    throw new Error('Server returned HTML instead of JSON. Please try again.');
                                }
                            }
                            
                            // Try to parse as JSON
                            try {
                                const data = JSON.parse(text);
                                if (data && data.status === 'success' && data.scan_id) {
                                    // Show completion message
                                    scanComplete.style.display = 'block';
                                    
                                    // Update the results button with correct URL from server
                                    const viewResultsBtn = document.querySelector('#scanComplete a.btn');
                                    viewResultsBtn.href = data.results_url || `/results?scan_id=${data.scan_id}`;
                                } else if (data && data.status === 'error') {
                                    // Show specific error from JSON
                                    throw new Error(data.message || 'Unknown error occurred');
                                } else {
                                    // Unexpected JSON format
                                    throw new Error('Invalid response format. Please try again.');
                                }
                            } catch (jsonError) {
                                // Log the parsing error and the raw response
                                console.error('JSON parsing error:', jsonError);
                                console.error('Raw response:', text);
                                throw new Error('Server returned invalid response. Please try again or contact support.');
                            }
                        });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while processing your scan: ' + error.message);
                        // Reset the form view
                        scanProgress.style.display = 'none';
                        scanForm.style.display = 'block';
                    });
                }, 14000); // This matches the total time of all progress animations
            });
        }"""
            
            content = content.replace(old_submission, new_submission)
            
            logger.info("✅ Updated scan form submission with better JSON handling")
    
    # Check if our fix script is already included
    if 'fix_scanner_json_parsing.js' not in content and '</body>' in content:
        # Add our script before </body>
        script_tag = '    <!-- Scanner JSON parsing fix -->\n    <script src="/static/js/fix_scanner_json_parsing.js"></script>\n</body>'
        content = content.replace('</body>', script_tag)
        logger.info("✅ Added fix_scanner_json_parsing.js to scan.html")
    
    # Write the updated file
    with open(scan_html_path, 'w') as f:
        f.write(content)
    
    return True

def fix_scanner_js():
    """Fix scanner.js to handle JSON parsing errors"""
    scanner_js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'js', 'scanner.js')
    
    if not os.path.exists(scanner_js_path):
        logger.warning(f"scanner.js not found at {scanner_js_path}")
        return False
    
    # Read the file
    with open(scanner_js_path, 'r') as f:
        content = f.read()
    
    # Add proper error handling to fetch calls
    # First check for fetch without error handling
    fetch_pattern = r'fetch\([\'\"]/api/scanner/(.*?)\);'
    
    # Find all fetch calls
    fetch_calls = re.findall(r'fetch\(.*?\).*?\.then\(', content, re.DOTALL)
    for fetch_call in fetch_calls:
        # Check if it already has error handling
        if 'catch(' not in fetch_call and '.catch' not in content[content.find(fetch_call):content.find(fetch_call) + 500]:
            # Get the whole function
            func_start = content.rfind('const', 0, content.find(fetch_call))
            func_end = content.find(';', content.find(fetch_call) + len(fetch_call))
            if func_start > 0 and func_end > func_start:
                function_code = content[func_start:func_end + 1]
                
                # Add error handling
                new_function_code = function_code.replace('.then(', '.then(response => {\n' + 
                                                          '        if (!response.ok) {\n' + 
                                                          '            throw new Error(`HTTP error! status: ${response.status}`);\n' + 
                                                          '        }\n' + 
                                                          '        return response;\n' + 
                                                          '    })' + 
                                                          '.then(')
                
                # Add catch handler if not present
                if '.catch(' not in new_function_code:
                    # Find last closing parenthesis
                    last_paren = new_function_code.rfind(')')
                    if last_paren > 0 and new_function_code[last_paren+1] == ';':
                        new_function_code = new_function_code[:last_paren+1] + '.catch(error => {\n' + \
                                           '        console.error("Error:", error);\n' + \
                                           '        return { success: false, error: error.message };\n' + \
                                           '    })' + new_function_code[last_paren+1:]
                
                # Update content
                content = content.replace(function_code, new_function_code)
    
    # Ensure we have proper handling of response.json()
    json_pattern = r'response\.json\(\)'
    json_calls = re.findall(json_pattern, content)
    
    for json_call in json_calls:
        # Check if it's already in a try-catch block
        pos = content.find(json_call)
        try_pos = content.rfind('try', 0, pos)
        catch_pos = content.find('catch', pos, pos + 500)
        
        if try_pos == -1 or catch_pos == -1 or try_pos < pos - 100:
            # Not in a try-catch, replace it
            safe_json = 'response.text().then(text => {\n' + \
                       '            try {\n' + \
                       '                return JSON.parse(text);\n' + \
                       '            } catch (e) {\n' + \
                       '                console.error("Error parsing JSON:", e);\n' + \
                       '                console.error("Raw response:", text);\n' + \
                       '                return { success: false, error: "Invalid server response format" };\n' + \
                       '            }\n' + \
                       '        })'
            
            content = content.replace(json_call, safe_json)
    
    # Write the updated file
    with open(scanner_js_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Fixed scanner.js with JSON parsing error handling")
    return True

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Comprehensive JSON Parsing Fix")
    print("=" * 80)
    
    # Fix scan routes
    if fix_scan_routes():
        print("✅ Fixed scan routes")
    else:
        print("❌ Failed to fix scan routes")
    
    # Update scan form
    if update_scan_form():
        print("✅ Updated scan form")
    else:
        print("❌ Failed to update scan form")
    
    # Fix scanner.js
    if fix_scanner_js():
        print("✅ Fixed scanner.js")
    else:
        print("❌ Failed to fix scanner.js")
    
    print("\nComprehensive JSON parsing fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()