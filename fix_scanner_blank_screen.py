#!/usr/bin/env python3
"""
Fix Scanner Blank Screen Issue
This script fixes issues causing the scanner to display blank after loading
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_scan_html():
    """Update scan.html template to fix JavaScript errors"""
    scan_html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'scan.html')
    
    if not os.path.exists(scan_html_path):
        logger.error(f"scan.html not found at {scan_html_path}")
        return False
    
    try:
        # Read the current file
        with open(scan_html_path, 'r') as f:
            content = f.read()
        
        # First check if our debug script is already included
        if 'scanner_debug.js' not in content:
            # Add the debug script before the existing scripts, after Bootstrap
            if 'bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js' in content:
                new_script = '    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>\n'
                new_script += '    <!-- Scanner Debug Script -->\n'
                new_script += '    <script src="/static/js/scanner_debug.js"></script>\n'
                
                # Replace the existing Bootstrap script with both scripts
                content = content.replace(
                    '    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>',
                    new_script
                )
                
                logger.info("✅ Added scanner_debug.js to scan.html")
        
        # Check for duplicate function definitions or script includes
        if content.count('function setupFormSteps()') > 1:
            logger.warning("⚠️ Found multiple setupFormSteps() definitions! Fixing...")
            
            # Extract the first complete setupFormSteps function
            import re
            match = re.search(r'function\s+setupFormSteps\(\)\s*\{.*?\}\s*;?\s*\n', content, re.DOTALL)
            if match:
                # Keep only the first instance
                setupFormSteps_first = match.group(0)
                
                # Replace subsequent instances with a call to the function
                pattern = r'function\s+setupFormSteps\(\)\s*\{.*?\}\s*;?\s*\n'
                remaining_content = content[match.end():]
                remaining_content = re.sub(pattern, '// setupFormSteps already defined\n', remaining_content, flags=re.DOTALL)
                
                # Reconstruct content
                content = content[:match.end()] + remaining_content
                
                logger.info("✅ Fixed duplicate setupFormSteps() definition")
        
        # Similarly check for duplicate setupFormSubmission
        if content.count('function setupFormSubmission()') > 1:
            logger.warning("⚠️ Found multiple setupFormSubmission() definitions! Fixing...")
            
            # Extract the first complete setupFormSubmission function
            import re
            match = re.search(r'function\s+setupFormSubmission\(\)\s*\{.*?\}\s*;?\s*\n', content, re.DOTALL)
            if match:
                # Keep only the first instance
                setupFormSubmission_first = match.group(0)
                
                # Replace subsequent instances with a call to the function
                pattern = r'function\s+setupFormSubmission\(\)\s*\{.*?\}\s*;?\s*\n'
                remaining_content = content[match.end():]
                remaining_content = re.sub(pattern, '// setupFormSubmission already defined\n', remaining_content, flags=re.DOTALL)
                
                # Reconstruct content
                content = content[:match.end()] + remaining_content
                
                logger.info("✅ Fixed duplicate setupFormSubmission() definition")
        
        # Add fallback error handling for blank screens
        if 'window.addEventListener(\'error\'' not in content:
            error_handler = """
    <script>
    // Global error handling to prevent blank screens
    window.addEventListener('error', function(e) {
        console.error('Global error caught:', e.message, e.filename, e.lineno);
        
        // If body is empty, show a recovery message
        if (document.body && !document.body.innerHTML.trim()) {
            document.body.innerHTML = `
                <div style="padding: 20px; background: #fff; color: #333; max-width: 800px; margin: 0 auto; font-family: Arial, sans-serif;">
                    <h1>Scanner Error</h1>
                    <p>The scanner encountered an error. Please try refreshing the page.</p>
                    <button onclick="window.location.reload()" style="padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin-top: 10px;">Refresh Page</button>
                </div>
            `;
        }
    });
    </script>
    """
            
            # Add before the closing </body> tag
            content = content.replace('</body>', error_handler + '</body>')
            logger.info("✅ Added global error handler to scan.html")
        
        # Write the updated file
        with open(scan_html_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated scan.html template")
        return True
    
    except Exception as e:
        logger.error(f"Error updating scan.html: {e}")
        return False

def fix_scanner_template_html():
    """Fix scanner_template.html if it exists"""
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'scanner_template.html')
    
    if not os.path.exists(template_path):
        logger.warning(f"scanner_template.html not found at {template_path}")
        return False
    
    try:
        # Read the current file
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Add our debug script if not already there
        if 'scanner_debug.js' not in content and '</body>' in content:
            script_tag = '    <!-- Scanner Debug Script -->\n    <script src="/static/js/scanner_debug.js"></script>\n</body>'
            content = content.replace('</body>', script_tag)
            logger.info("✅ Added scanner_debug.js to scanner_template.html")
        
        # Write the updated file
        with open(template_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated scanner_template.html")
        return True
    
    except Exception as e:
        logger.error(f"Error updating scanner_template.html: {e}")
        return False

def add_safety_to_fix_json_parsing_js():
    """Update fix_scanner_json_parsing.js to be more defensive"""
    js_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'js', 'fix_scanner_json_parsing.js')
    
    if not os.path.exists(js_path):
        logger.warning(f"fix_scanner_json_parsing.js not found at {js_path}")
        return False
    
    try:
        # Read the current file
        with open(js_path, 'r') as f:
            content = f.read()
        
        # Add a safety check to prevent breaking the page
        if 'window.addEventListener(\'error\'' not in content:
            safety_code = """
// Global error handler to prevent script from breaking page
window.addEventListener('error', function(e) {
    if (e.filename && e.filename.includes('fix_scanner_json_parsing.js')) {
        console.error('Error in JSON parsing fix script:', e.message);
        console.error('Error location:', e.filename, 'line', e.lineno, 'column', e.colno);
        // Don't let our utility script break the page
        e.preventDefault();
        return true;
    }
});
"""
            # Add at the beginning of the file
            content = safety_code + content
            logger.info("✅ Added safety error handler to fix_scanner_json_parsing.js")
        
        # Make document.querySelectorAll more defensive
        if 'document.querySelectorAll(\'form\')' in content:
            # Add try-catch around the form enhancement
            enhance_forms_code = "document.querySelectorAll('form').forEach(form => {"
            safe_enhance_forms = """try {
    document.querySelectorAll('form').forEach(form => {"""
            
            if content.count(enhance_forms_code) == 1:
                # Replace with safer version
                content = content.replace(
                    enhance_forms_code, 
                    safe_enhance_forms
                )
                # Add closing try-catch
                content = content.replace(
                    "        }\n    });", 
                    "        }\n    });\n} catch (formError) {\n    console.error('Error enhancing forms:', formError);\n}"
                )
                logger.info("✅ Made form enhancement code more defensive")
        
        # Write the updated file
        with open(js_path, 'w') as f:
            f.write(content)
        
        logger.info("✅ Updated fix_scanner_json_parsing.js with safety features")
        return True
    
    except Exception as e:
        logger.error(f"Error updating fix_scanner_json_parsing.js: {e}")
        return False

def main():
    """Main function to fix scanner blank screen issues"""
    print("\n" + "=" * 80)
    print(" Scanner Blank Screen Fix")
    print("=" * 80)
    
    # Update scan.html to include debug script
    if update_scan_html():
        print("✅ Updated scan.html template")
    else:
        print("❌ Failed to update scan.html template")
    
    # Fix scanner_template.html
    if fix_scanner_template_html():
        print("✅ Fixed scanner_template.html")
    else:
        print("❌ Failed to fix scanner_template.html")
    
    # Make JSON parsing fix script more defensive
    if add_safety_to_fix_json_parsing_js():
        print("✅ Enhanced fix_scanner_json_parsing.js with safety features")
    else:
        print("❌ Failed to enhance fix_scanner_json_parsing.js")
    
    print("\nScanner blank screen fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()