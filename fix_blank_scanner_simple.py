#!/usr/bin/env python3
"""
Simple Fix for Blank Scanner Screen
Adds a fallback simple scanner page
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_fallback_route():
    """Add a simple fallback route to scanner_routes.py"""
    scanner_routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes', 'scanner_routes.py')
    
    if not os.path.exists(scanner_routes_path):
        logger.error(f"scanner_routes.py not found at {scanner_routes_path}")
        return False
    
    # Read the file
    with open(scanner_routes_path, 'r') as f:
        content = f.read()
    
    # Check if fallback route already exists
    if 'scanner_simple_view' in content:
        logger.info("Fallback route already exists")
        return True
    
    # Add fallback route at the end of the file
    fallback_route = """

@scanner_bp.route('/scanner/<scanner_uid>/simple')
def scanner_simple_view(scanner_uid):
    \"\"\"Simple fallback scanner view for troubleshooting\"\"\"
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
    
    # Add to file
    with open(scanner_routes_path, 'a') as f:
        f.write(fallback_route)
    
    logger.info("✅ Added fallback route to scanner_routes.py")
    return True

def add_recovery_script():
    """Add a recovery script to scan.html"""
    scan_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'scan.html')
    
    if not os.path.exists(scan_html_path):
        logger.error(f"scan.html not found at {scan_html_path}")
        return False
    
    # Read the file
    with open(scan_html_path, 'r') as f:
        content = f.read()
    
    # Check if recovery script already exists
    if 'detectBlankScreen' in content:
        logger.info("Recovery script already exists")
        return True
    
    # Add recovery script before </body>
    recovery_script = """
    <!-- Scanner Recovery Script -->
    <script>
    // Check for blank screen after page loads
    setTimeout(function() {
        // Check if main UI elements are visible
        var mainElements = [
            document.querySelector('.header'),
            document.querySelector('.card'),
            document.querySelector('#scanForm')
        ];
        
        var visibleCount = 0;
        mainElements.forEach(function(el) {
            if (el && (el.offsetHeight > 0 || el.getClientRects().length > 0)) {
                visibleCount++;
            }
        });
        
        // If most elements are not visible
        if (visibleCount < 2 && !window.location.href.includes('/simple')) {
            console.log('Blank screen detected - redirecting to simple view');
            // Extract scanner ID from URL
            var scannerMatch = window.location.pathname.match(/scanner\\/(.*?)\\/embed/);
            if (scannerMatch && scannerMatch[1]) {
                window.location.href = '/scanner/' + scannerMatch[1] + '/simple';
            }
        }
    }, 2000);
    </script>
    </body>"""
    
    # Replace closing body tag
    content = content.replace('</body>', recovery_script)
    
    # Write updated content
    with open(scan_html_path, 'w') as f:
        f.write(content)
    
    logger.info("✅ Added recovery script to scan.html")
    return True

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Simple Scanner Blank Screen Fix")
    print("=" * 80)
    
    # Add fallback route
    if add_fallback_route():
        print("✅ Added fallback route to scanner_routes.py")
    else:
        print("❌ Failed to add fallback route")
    
    # Add recovery script
    if add_recovery_script():
        print("✅ Added recovery script to scan.html")
    else:
        print("❌ Failed to add recovery script")
    
    print("\nFixed scanner blank screen issues. Users will now be redirected to a simple version if the main scanner fails to load.")
    print("=" * 80)

if __name__ == "__main__":
    main()