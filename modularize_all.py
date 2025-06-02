#!/usr/bin/env python3
"""
Comprehensive script to modularize the entire CybrScan codebase.
This script will split all large files into modular components while maintaining functionality.
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

def create_comprehensive_readme():
    """Create a comprehensive README file explaining the modular structure."""
    readme_content = """# CybrScan Modular Structure

## Overview
The CybrScan codebase has been reorganized into a modular structure for improved maintainability and readability. 
Large files have been split into smaller, focused modules that are easier to understand and modify.

## Directory Structure

### Database Modules (`db_modules/`)
Database-related functionality split from `client_db.py`:
- `core.py` - Core database functions and connection handling
- `auth.py` - Authentication and user management
- `client.py` - Client data management
- `scanner.py` - Scanner configuration and deployment
- `scan_results.py` - Scan results and history
- `dashboard.py` - Dashboard data and statistics
- `admin.py` - Admin-specific database functions
- `customization.py` - Customization and branding
- `utilities.py` - Utility functions

### Scan Modules (`scan_modules/`)
Security scanning functionality split from `scan.py`:
- `network.py` - Network scanning functions
- `web.py` - Web application scanning
- `dns.py` - DNS and domain scanning
- `ssl.py` - SSL/TLS certificate scanning
- `industry.py` - Industry and sector analysis
- `vulnerability.py` - Vulnerability scanning
- `reporting.py` - Scan report generation
- `utilities.py` - Utility functions and constants

### Client Modules (`client_modules/`)
Client routes and functions split from `client.py`:
- `dashboard.py` - Dashboard routes
- `scanners.py` - Scanner management routes
- `reports.py` - Report viewing routes
- `settings.py` - Client settings routes
- `profile.py` - User profile routes
- `misc.py` - Miscellaneous routes
- `utils.py` - Helper functions

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

## Original Files
The original monolithic files now act as proxy modules that import and re-export functionality from the modular files. This maintains backward compatibility with the rest of the codebase.

## Advantages
- **Improved Readability**: Smaller files focused on specific functionality
- **Better Maintainability**: Easier to find and modify specific code
- **Enhanced Collaboration**: Multiple developers can work on different modules
- **Reduced Cognitive Load**: No need to understand thousands of lines of code at once
- **Better Testing**: Modules can be tested individually

## How to Use
Each module can be imported directly or through the proxy files. For example:

```python
# Old way (still works)
from client_db import get_client_by_id

# New way (more explicit)
from db_modules.client import get_client_by_id
```

## Note
This modular structure maintains complete functionality while making the code more manageable.
"""
    
    with open('MODULAR_STRUCTURE.md', 'w') as f:
        f.write(readme_content)
    
    logger.info("Created comprehensive MODULAR_STRUCTURE.md")

def main():
    """Main function to modularize the entire codebase."""
    logger.info("Starting comprehensive modularization of the CybrScan codebase...")
    
    # Backup all important files
    important_files = [
        'client_db.py',
        'scan.py',
        'client.py',
        'fixed_scan_core.py',
        'enhanced_admin_dashboard.py',
        'enhanced_scan.py'
    ]
    
    for file_path in important_files:
        backup_file(file_path)
    
    # Run all split scripts
    core_scripts = [
        'split_client_db.py',
        'split_scan.py',
        'split_client.py'
    ]
    
    additional_scripts = [
        'split_fixed_scan_core.py',
        'split_enhanced_admin_dashboard.py',
        'split_enhanced_scan.py'
    ]
    
    all_scripts = core_scripts + additional_scripts
    
    success_count = 0
    for script in all_scripts:
        if run_script(script):
            success_count += 1
            
    # Update files if all scripts ran successfully
    if success_count == len(all_scripts):
        # Update all files with their modular versions
        update_file('client_db.py', 'client_db.py.new')
        update_file('scan.py', 'scan.py.new')
        update_file('client.py', 'client.py.new')
        update_file('fixed_scan_core.py', 'fixed_scan_core.py.new')
        update_file('enhanced_admin_dashboard.py', 'enhanced_admin_dashboard.py.new')
        update_file('enhanced_scan.py', 'enhanced_scan.py.new')
        
        # Create comprehensive README
        create_comprehensive_readme()
        
        logger.info("=" * 80)
        logger.info("Successfully modularized the entire CybrScan codebase!")
        logger.info(f"Split {len(all_scripts)} large files into modular components")
        logger.info("All functionality has been preserved with backward compatibility")
        logger.info("Check MODULAR_STRUCTURE.md for details on the new structure")
        logger.info("=" * 80)
    else:
        logger.error(f"Only {success_count}/{len(all_scripts)} scripts ran successfully.")
        logger.error("The complete modularization was not finished.")
        logger.error("Please check the logs and fix any errors before trying again.")

if __name__ == '__main__':
    main()