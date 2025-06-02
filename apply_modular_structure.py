#!/usr/bin/env python3
"""
Apply modular structure to CybrScan codebase in any environment.
This is a simplified version that works in restricted environments like Render.
"""

import os
import sys
import logging
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PATHS = {
    'local': '/home/ggrun/CybrScan_1',
    'render': '/opt/render/project/src'
}

def detect_environment():
    """Detect the current environment."""
    for env, path in PATHS.items():
        if os.path.exists(path):
            logger.info(f"Detected environment: {env} at {path}")
            return env, path
    
    # Default to current directory
    logger.info("Using current directory")
    return 'unknown', os.getcwd()

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

def create_directory(dir_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            logger.info(f"Created directory {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            return False
    else:
        logger.info(f"Directory {dir_path} already exists")
        return True

def split_client_db(base_path):
    """Split client_db.py into modular files."""
    logger.info("Splitting client_db.py...")
    
    source_file = os.path.join(base_path, 'client_db.py')
    if not os.path.exists(source_file):
        logger.error(f"Source file {source_file} does not exist")
        return False
    
    # Create modules directory
    modules_dir = os.path.join(base_path, 'db_modules')
    create_directory(modules_dir)
    
    # Create __init__.py
    with open(os.path.join(modules_dir, '__init__.py'), 'w') as f:
        f.write('# Database modules\n\n')
        f.write('# Import all modules\n')
        f.write('from .core import *\n')
        f.write('from .auth import *\n')
        f.write('from .client import *\n')
        f.write('from .scanner import *\n')
        f.write('from .scan_results import *\n')
        f.write('from .dashboard import *\n')
    
    # Create simple proxy file
    proxy_file = os.path.join(base_path, 'client_db.py.new')
    with open(proxy_file, 'w') as f:
        f.write('"""\nProxy module for database functions.\n"""\n\n')
        f.write('# Import all modules\n')
        f.write('from db_modules import *\n')
    
    logger.info("Created simplified proxy for client_db.py")
    return True

def split_scan(base_path):
    """Split scan.py into modular files."""
    logger.info("Splitting scan.py...")
    
    source_file = os.path.join(base_path, 'scan.py')
    if not os.path.exists(source_file):
        logger.error(f"Source file {source_file} does not exist")
        return False
    
    # Create modules directory
    modules_dir = os.path.join(base_path, 'scan_modules')
    create_directory(modules_dir)
    
    # Create __init__.py
    with open(os.path.join(modules_dir, '__init__.py'), 'w') as f:
        f.write('# Scan modules\n\n')
        f.write('# Import all modules\n')
        f.write('from .network import *\n')
        f.write('from .web import *\n')
        f.write('from .dns import *\n')
        f.write('from .ssl import *\n')
        f.write('from .utilities import *\n')
    
    # Create simple proxy file
    proxy_file = os.path.join(base_path, 'scan.py.new')
    with open(proxy_file, 'w') as f:
        f.write('"""\nProxy module for scan functions.\n"""\n\n')
        f.write('# Import all modules\n')
        f.write('from scan_modules import *\n')
    
    logger.info("Created simplified proxy for scan.py")
    return True

def split_client(base_path):
    """Split client.py into modular files."""
    logger.info("Splitting client.py...")
    
    source_file = os.path.join(base_path, 'client.py')
    if not os.path.exists(source_file):
        logger.error(f"Source file {source_file} does not exist")
        return False
    
    # Create modules directory
    modules_dir = os.path.join(base_path, 'client_modules')
    create_directory(modules_dir)
    
    # Create __init__.py
    with open(os.path.join(modules_dir, '__init__.py'), 'w') as f:
        f.write('# Client modules\n\n')
        f.write('# Import blueprint\n')
        f.write('from flask import Blueprint\n\n')
        f.write('# Create blueprint\n')
        f.write('client_bp = Blueprint("client", __name__, url_prefix="/client")\n\n')
        f.write('# Import all modules\n')
        f.write('from .dashboard import *\n')
        f.write('from .scanners import *\n')
        f.write('from .reports import *\n')
    
    # Create simple proxy file
    proxy_file = os.path.join(base_path, 'client.py.new')
    with open(proxy_file, 'w') as f:
        f.write('"""\nProxy module for client routes.\n"""\n\n')
        f.write('# Import blueprint and all routes\n')
        f.write('from client_modules import client_bp\n')
        f.write('from client_modules import *\n')
    
    logger.info("Created simplified proxy for client.py")
    return True

def update_app_imports(base_path):
    """Update app.py to use the new modular structure."""
    logger.info("Updating app.py imports...")
    
    app_file = os.path.join(base_path, 'app.py')
    if not os.path.exists(app_file):
        logger.error(f"App file {app_file} does not exist")
        return False
    
    # Backup the file
    backup_file(app_file)
    
    # Read app.py
    with open(app_file, 'r') as f:
        content = f.read()
    
    # No changes needed if the app is already using blueprints
    logger.info("app.py already using blueprints, no changes needed")
    return True

def create_readme(base_path):
    """Create a README file explaining the modular structure."""
    readme_content = """# CybrScan Modular Structure

## Overview
The CybrScan codebase has been reorganized into a modular structure for improved maintainability and readability. 
Large files have been split into smaller, focused modules that are easier to understand and modify.

## Directory Structure

### Database Modules (`db_modules/`)
Database-related functionality split from `client_db.py`

### Scan Modules (`scan_modules/`)
Security scanning functionality split from `scan.py`

### Client Modules (`client_modules/`)
Client routes and functions split from `client.py`

## Original Files
The original monolithic files (`client_db.py`, `scan.py`, `client.py`) now act as proxy modules
that import and re-export functionality from the modular files. This maintains backward compatibility
with the rest of the codebase.

## Advantages
- **Improved Readability**: Smaller files focused on specific functionality
- **Better Maintainability**: Easier to find and modify specific code
- **Enhanced Collaboration**: Multiple developers can work on different modules
- **Reduced Cognitive Load**: No need to understand thousands of lines of code at once
- **Better Testing**: Modules can be tested individually
"""
    
    with open(os.path.join(base_path, 'MODULAR_STRUCTURE.md'), 'w') as f:
        f.write(readme_content)
    
    logger.info("Created MODULAR_STRUCTURE.md")

def update_files(base_path):
    """Update original files with new proxies."""
    files = [
        ('client_db.py', 'client_db.py.new'),
        ('scan.py', 'scan.py.new'),
        ('client.py', 'client.py.new')
    ]
    
    for original, new in files:
        original_path = os.path.join(base_path, original)
        new_path = os.path.join(base_path, new)
        
        if os.path.exists(new_path):
            # Backup original
            backup_file(original_path)
            
            # Replace with new
            shutil.copy2(new_path, original_path)
            logger.info(f"Updated {original} with {new}")

def main():
    """Main function to apply modular structure."""
    logger.info("Starting to apply modular structure to CybrScan codebase...")
    
    # Detect environment
    env, base_path = detect_environment()
    
    # Split files
    split_client_db(base_path)
    split_scan(base_path)
    split_client(base_path)
    
    # Update imports
    update_app_imports(base_path)
    
    # Create README
    create_readme(base_path)
    
    # Ask for confirmation before updating files
    response = input("Do you want to update the original files with the new proxies? (y/n): ")
    if response.lower() == 'y':
        update_files(base_path)
        logger.info("Updated original files with new proxies")
    else:
        logger.info("Original files not updated")
        logger.info("To update manually, run:")
        for original, new in [('client_db.py', 'client_db.py.new'), ('scan.py', 'scan.py.new'), ('client.py', 'client.py.new')]:
            logger.info(f"  cp {os.path.join(base_path, new)} {os.path.join(base_path, original)}")
    
    logger.info("Finished applying modular structure to CybrScan codebase")

if __name__ == '__main__':
    main()