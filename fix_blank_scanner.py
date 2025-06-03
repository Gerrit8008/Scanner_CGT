#!/usr/bin/env python3
"""
Emergency Fix for Scanner Blank Screen Issue
This script creates a fallback route for scanners when the main page has issues
"""

import os
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_fallback_route():
    """Add a fallback route for scanners with simplified UI"""
    # Look for routes/scanner_routes.py and add a fallback route
    scanner_routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'scanner_routes.py')
    
    if not os.path.exists(scanner_routes_path):
        logger.error(f"scanner_routes.py not found at {scanner_routes_path}")
        return False
    
    # Read the current content
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Check if fallback route already exists
    if '@scanner_bp.route(\'/scanner/<scanner_uid>/simple\')' in content:
        logger.info("Fallback route already exists")
        return True
    
    # Find the last route definition
    route_matches = re.findall(r'@scanner_bp\.route\(.*?\)\s*def\s+(\w+).*?:', content, re.DOTALL)
    
    if not route_matches:
        logger.error("Could not find any route definitions in scanner_routes.py")
        return False
    
    # Find the last route function
    last_route = route_matches[-1]
    
    # Find the end of this function to add our new route after it
    func_pattern = f"def\\s+{last_route}.*?\\n\\n\\n"
    func_match = re.search(func_pattern, content, re.DOTALL)
    
    if not func_match:
        # Try alternative pattern if we don't find two newlines at the end
        func_pattern = f"def\\s+{last_route}.*?return.*?\\n"
        func_match = re.search(func_pattern, content, re.DOTALL)
        
        if not func_match:
            logger.error(f"Could not find the end of function {last_route}")
            return False
    
    # Get insert position
    insert_pos = func_match.end()
    
    # Prepare the new route
    fallback_route = """

@scanner_bp.route('/scanner/<scanner_uid>/simple')
def scanner_simple_view(scanner_uid):
    """Simple fallback scanner view for troubleshooting"""
    try:
        # Get basic scanner data
        from client_db import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, client_id FROM scanners WHERE scanner_id = ?', (scanner_uid,))
        scanner_row = cursor.fetchone()
        conn.close()
        
        if scanner_row:
            # Convert to dict for easier access
            if hasattr(scanner_row, 'keys'):
                scanner_data = dict(scanner_row)
            else:
                scanner_data = dict(zip(['id', 'client_id'], scanner_row))
                
            # Render the simple template
            return render_template('simple_scan.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid,
                                client_id=scanner_data.get('client_id'))
        else:
            # Scanner not found
            return render_template('simple_scan.html', 
                                scanner_uid=scanner_uid,
                                scanner_id=scanner_uid)
    
    except Exception as e:
        logging.error(f"Error in simple scanner view: {e}")
        # Absolute fallback - render with minimal data
        return render_template('simple_scan.html', 
                            scanner_uid=scanner_uid,
                            scanner_id=scanner_uid)
"""
    
    # Add triple quotes to the docstring
    fallback_route = fallback_route.replace('"""Simple fallback', '"""Simple fallback')
    
    # Insert the new route
    new_content = content[:insert_pos] + fallback_route + content[insert_pos:]
    
    # Write the updated file
    with open(scanner_routes_path, 'w') as f:
        f.write(new_content)
    
    logger.info("✅ Added simple fallback route to scanner_routes.py")
    return True

def add_redirect_to_scan_page():
    """Add a recovery redirect to scan.html to handle blank screen issues"""
    scan_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'scan.html')
    
    if not os.path.exists(scan_html_path):
        logger.error(f"scan.html not found at {scan_html_path}")
        return False
    
    # Read the current content
    with open(scan_html_path, 'r') as f:
        content = f.read()
    
    # Check if we already added the recovery redirect
    if 'function detectBlankScreen()' in content:
        logger.info("Recovery redirect already exists in scan.html")
        return True
    
    # Add recovery script after existing scripts
    recovery_script = """
    <!-- Scanner Recovery Script -->
    <script>
    function detectBlankScreen() {
        // Check if main UI elements are visible
        var mainElements = [
            document.querySelector('.header'),
            document.querySelector('.card-body'),
            document.querySelector('#scanForm')
        ];
        
        var visibleCount = mainElements.filter(function(el) {
            return el && (el.offsetHeight > 0 || el.getClientRects().length > 0);
        }).length;
        
        // If most elements are not visible
        if (visibleCount < 2) {
            console.log('Detected potentially blank screen - ' + visibleCount + ' visible elements');
            
            // Check if URL contains 'simple'
            if (window.location.href.indexOf('/simple') === -1) {
                console.log('Redirecting to simple scanner view');
                // Get scanner ID from URL
                var scannerMatch = window.location.href.match(/scanner\\/([a-zA-Z0-9_-]+)/);
                if (scannerMatch && scannerMatch[1]) {
                    var scannerId = scannerMatch[1];
                    // Redirect to simple view
                    window.location.href = '/scanner/' + scannerId + '/simple';
                }
            }
        }
    }
    
    // Wait 3 seconds after page load to check
    setTimeout(detectBlankScreen, 3000);
    </script>
    """
    
    # Add before closing body
    content = content.replace('</body>', recovery_script + '</body>')
    
    # Write the updated file
    with open(scan_html_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Added blank screen recovery redirect to scan.html")
    return True

def main():
    """Main function to fix scanner blank screen issues"""
    print("\n" + "=" * 80)
    print(" Emergency Scanner Fix")
    print("=" * 80)
    
    # Add fallback route
    if add_fallback_route():
        print("✅ Added simple fallback route")
    else:
        print("❌ Failed to add fallback route")
    
    # Add recovery redirect
    if add_redirect_to_scan_page():
        print("✅ Added blank screen recovery redirect")
    else:
        print("❌ Failed to add recovery redirect")
    
    print("\nEmergency scanner fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()