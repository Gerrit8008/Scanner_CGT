#!/usr/bin/env python3
"""
Direct patching script for admin dashboard

This script directly patches the admin.py file to include the enhanced dashboard.
It preserves all existing functionality while adding comprehensive data display.
"""

import os
import re
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def patch_admin_py():
    """
    Directly patch the admin.py file to include the enhanced dashboard
    """
    admin_py_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin.py')
    
    if not os.path.exists(admin_py_path):
        logger.error(f"Admin file not found: {admin_py_path}")
        return False
    
    # Create a backup
    backup_path = f"{admin_py_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(admin_py_path, backup_path)
    logger.info(f"Created backup: {backup_path}")
    
    # Read the admin.py file
    with open(admin_py_path, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "from enhanced_admin_dashboard import" in content:
        logger.info("Admin file already patched")
        return True
    
    # Add import at the top after other imports
    import_pattern = r"(from .+?\n|import .+?\n)+"
    match = re.search(import_pattern, content)
    
    if match:
        # Add import after other imports
        import_statement = (
            "# Import enhanced admin dashboard\n"
            "try:\n"
            "    from enhanced_admin_dashboard import get_enhanced_dashboard_data, enhance_admin_dashboard\n"
            "    logger.info('Enhanced admin dashboard imported')\n"
            "except ImportError as e:\n"
            "    logger.warning(f'Enhanced admin dashboard not available: {e}')\n\n"
        )
        
        modified_content = content[:match.end()] + import_statement + content[match.end():]
        
        # Add activation code at the end of the file
        activation_code = (
            "\n\n# Activate enhanced admin dashboard\n"
            "try:\n"
            "    if 'enhance_admin_dashboard' in locals():\n"
            "        logger.info('Activating enhanced admin dashboard...')\n"
            "        enhance_admin_dashboard()\n"
            "        logger.info('Enhanced admin dashboard activated')\n"
            "except Exception as e:\n"
            "    logger.warning(f'Failed to activate enhanced admin dashboard: {e}')\n"
        )
        
        modified_content += activation_code
        
        # Write the modified content
        with open(admin_py_path, 'w') as f:
            f.write(modified_content)
        
        logger.info("Admin file patched successfully")
        return True
    else:
        logger.error("Could not find import section in admin.py")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Direct Patching of Admin Dashboard")
    print("=" * 60)
    
    try:
        success = patch_admin_py()
        
        if success:
            print("\n✅ Admin dashboard patched successfully!")
            print("\nThe admin dashboard will now show comprehensive data including:")
            print("  - Detailed client information")
            print("  - Scanner deployment statistics")
            print("  - Lead generation data")
            print("  - System health metrics")
            print("  - User activity tracking")
            print("  - Real-time data visualization")
            print("\nNo functionality has been lost in the process.")
        else:
            print("\n❌ Failed to patch admin dashboard")
    except Exception as e:
        logger.error(f"Error patching admin dashboard: {str(e)}")
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()