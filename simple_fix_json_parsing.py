#!/usr/bin/env python3
"""
Simple fix for JSON parsing errors in scanner routes
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_json_parsing_script():
    """Add the fix_scanner_json_parsing.js script to scanner templates"""
    templates_to_update = [
        'scan.html',
        'scanner_template.html'
    ]
    
    for template_name in templates_to_update:
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', template_name)
        
        if not os.path.exists(template_path):
            logger.warning(f"Template {template_name} not found at {template_path}")
            continue
        
        # Read the template
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check if our script is already included
        if 'fix_scanner_json_parsing.js' in content:
            logger.info(f"Script already included in {template_name}")
            continue
        
        # Find the right place to add our script - before </body>
        if '</body>' in content:
            # Add before </body>
            new_content = content.replace('</body>', 
                                        '    <!-- Scanner JSON parsing fix -->\n'
                                        '    <script src="/static/js/fix_scanner_json_parsing.js"></script>\n'
                                        '</body>')
            
            # Write the updated template
            with open(template_path, 'w') as f:
                f.write(new_content)
            
            logger.info(f"✅ Added fix_scanner_json_parsing.js to {template_name}")
        else:
            logger.warning(f"Could not find </body> tag in {template_name}")

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Simple JSON Parsing Fix")
    print("=" * 80)
    
    # Add the script to scanner templates
    add_json_parsing_script()
    
    print("\nJSON parsing fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()