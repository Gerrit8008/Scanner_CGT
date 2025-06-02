#!/usr/bin/env python3
"""
Master script to modularize additional large files in the CybrScan codebase.
This script will split more large files into modular components while maintaining functionality.
"""

import os
import sys
import logging
import shutil
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_file(file_path):
    """Create a backup of a file."""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup of {os.path.basename(file_path)} at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup of {file_path}: {e}")
            return False
    else:
        logger.warning(f"File {file_path} does not exist, no backup created")
        return False

def run_script(script_path):
    """Run a Python script."""
    logger.info(f"Running {script_path}...")
    try:
        # Check if script exists
        if not os.path.exists(script_path):
            logger.error(f"Script {script_path} does not exist")
            return False
        
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Successfully ran {script_path}")
            logger.info(result.stdout)
            return True
        else:
            logger.error(f"Failed to run {script_path}")
            logger.error(result.stderr)
            return False
    except Exception as e:
        logger.error(f"Error running {script_path}: {e}")
        return False

def update_file(old_path, new_path):
    """Replace old file with new file."""
    try:
        if not os.path.exists(new_path):
            logger.error(f"New file {new_path} does not exist")
            return False
        
        # Backup the old file
        backup_file(old_path)
        
        # Replace old file with new file
        shutil.copy2(new_path, old_path)
        logger.info(f"Successfully updated {old_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating {old_path}: {e}")
        return False

def update_readme():
    """Update the MODULAR_STRUCTURE.md file with additional modules."""
    readme_path = 'MODULAR_STRUCTURE.md'
    
    if not os.path.exists(readme_path):
        # Create a new README if it doesn't exist
        with open(readme_path, 'w') as f:
            f.write("# CybrScan Modular Structure\n\n")
    
    # Additional content to append
    additional_content = """
## Additional Modules

### Fixed Scan Core Modules (`scan_core_modules/`)
Split from `fixed_scan_core.py`:
- `core.py` - Core classes and progress tracking
- `network.py` - Network scanning functionality
- `web.py` - Web application scanning
- `dns.py` - DNS and domain scanning
- `ssl.py` - SSL/TLS scanning
- `reporting.py` - Result formatting and reporting
- `utils.py` - Utility functions

### Enhanced Admin Dashboard Modules (`admin_dashboard_modules/`)
Split from `enhanced_admin_dashboard.py`:
- `core.py` - Main dashboard functions
- `clients.py` - Client-related functions
- `scanners.py` - Scanner-related functions
- `leads.py` - Lead-related functions
- `stats.py` - Statistical functions
- `system.py` - System health functions
- `reports.py` - Reporting functions
- `utils.py` - Utility functions

### Enhanced Scan Modules (`enhanced_scan_modules/`)
Split from `enhanced_scan.py`:
- `progress_tracking.py` - Progress tracking and real-time updates
- `network_scan.py` - Network scanning components
- `web_scan.py` - Web application scanning
- `dns_scan.py` - DNS and domain scanning
- `ssl_scan.py` - SSL/TLS certificate scanning
- `vulnerability_scan.py` - Vulnerability detection
- `results.py` - Result processing and formatting
- `utils.py` - Utility functions
"""
    
    # Append to the README
    with open(readme_path, 'a') as f:
        f.write(additional_content)
    
    logger.info(f"Updated {readme_path} with additional modules")

def main():
    """Main function to modularize additional files."""
    logger.info("Starting to modularize additional large files in the CybrScan codebase...")
    
    # Backup important files
    backup_file('fixed_scan_core.py')
    backup_file('enhanced_admin_dashboard.py')
    backup_file('enhanced_scan.py')
    
    # Run split scripts
    scripts = [
        'split_fixed_scan_core.py',
        'split_enhanced_admin_dashboard.py',
        'split_enhanced_scan.py'
    ]
    
    success_count = 0
    for script in scripts:
        if run_script(script):
            success_count += 1
    
    # Update files if all scripts ran successfully
    if success_count == len(scripts):
        update_file('fixed_scan_core.py', 'fixed_scan_core.py.new')
        update_file('enhanced_admin_dashboard.py', 'enhanced_admin_dashboard.py.new')
        update_file('enhanced_scan.py', 'enhanced_scan.py.new')
        
        # Update README
        update_readme()
        
        logger.info("Successfully modularized additional large files!")
        logger.info("Check MODULAR_STRUCTURE.md for details on the new structure.")
    else:
        logger.error(f"Only {success_count}/{len(scripts)} scripts ran successfully.")
        logger.error("The modularization of additional files was not completed.")
        logger.error("Please check the logs and fix any errors before trying again.")

if __name__ == '__main__':
    main()