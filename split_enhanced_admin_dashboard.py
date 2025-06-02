#!/usr/bin/env python3
"""
Split enhanced_admin_dashboard.py into smaller, modular files while maintaining functionality.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the directory structure
ADMIN_DASHBOARD_MODULES_DIR = 'admin_dashboard_modules'
os.makedirs(ADMIN_DASHBOARD_MODULES_DIR, exist_ok=True)

# Create __init__.py in admin_dashboard_modules directory
with open(os.path.join(ADMIN_DASHBOARD_MODULES_DIR, '__init__.py'), 'w') as f:
    f.write('# Admin dashboard modules package\n')

def extract_function_blocks(content):
    """Extract function definitions from content."""
    # Pattern to match function definitions
    func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    
    # Find all function definitions
    matches = list(re.finditer(func_pattern, content, re.MULTILINE))
    
    functions = []
    for i, match in enumerate(matches):
        func_name = match.group(1)
        start_pos = match.start()
        
        # Find end of the function (either the next function or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the function
        func_block = content[start_pos:end_pos].strip()
        functions.append((func_name, func_block))
    
    return functions

def categorize_functions(functions):
    """Categorize functions into modules based on their names and functionality."""
    categories = {
        'core': [],  # Main dashboard functions
        'clients': [],  # Client-related functions
        'scanners': [],  # Scanner-related functions
        'leads': [],  # Lead-related functions
        'stats': [],  # Statistical functions
        'system': [],  # System health functions
        'reports': [],  # Reporting functions
        'utils': [],  # Utility functions
    }
    
    for func_name, func_block in functions:
        if 'dashboard' in func_name or 'get_enhanced_' in func_name:
            categories['core'].append((func_name, func_block))
        elif 'client' in func_name:
            categories['clients'].append((func_name, func_block))
        elif 'scanner' in func_name or 'scan_' in func_name:
            categories['scanners'].append((func_name, func_block))
        elif 'lead' in func_name or 'conversion' in func_name:
            categories['leads'].append((func_name, func_block))
        elif 'statistic' in func_name or 'stats' in func_name or 'count' in func_name:
            categories['stats'].append((func_name, func_block))
        elif 'system' in func_name or 'health' in func_name or 'usage' in func_name:
            categories['system'].append((func_name, func_block))
        elif 'report' in func_name or 'generate' in func_name or 'format' in func_name:
            categories['reports'].append((func_name, func_block))
        else:
            categories['utils'].append((func_name, func_block))
    
    return categories

def create_module_files(categories, imports):
    """Create module files for each category."""
    for category, functions in categories.items():
        if not functions:
            logger.info(f"Skipping empty category: {category}")
            continue
        
        # Generate file content
        file_content = f'''"""
Admin dashboard module for {category} functionality.
Generated from enhanced_admin_dashboard.py
"""

{imports}

'''
        
        # Add functions
        for func_name, func_block in functions:
            file_content += func_block + "\n\n"
        
        # Write to file
        file_path = os.path.join(ADMIN_DASHBOARD_MODULES_DIR, f"{category}.py")
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        logger.info(f"Created {file_path} with {len(functions)} functions")

def create_proxy_module():
    """Create a proxy enhanced_admin_dashboard.py that imports from modular files."""
    with open('enhanced_admin_dashboard.py.new', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Enhanced Admin Dashboard Module

This module provides comprehensive data gathering functionality for the admin dashboard,
including detailed information about clients, scanners, leads, and system health.
This file imports and re-exports functions from modular files.
"""

import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta
import socket
import platform
import re
from pathlib import Path

# Import required modules
from client_db import get_db_connection
import scanner_db_functions
import admin_db_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all functions from modular files
from admin_dashboard_modules.core import *
from admin_dashboard_modules.clients import *
from admin_dashboard_modules.scanners import *
from admin_dashboard_modules.leads import *
from admin_dashboard_modules.stats import *
from admin_dashboard_modules.system import *
from admin_dashboard_modules.reports import *
from admin_dashboard_modules.utils import *
''')
    
    logger.info("Created enhanced_admin_dashboard.py.new proxy file")

def extract_imports(content):
    """Extract import statements from content."""
    imports_pattern = r'import.*?(?=def|class|\n\n)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)
    
    if imports_match:
        return imports_match.group(0).strip()
    return ""

def main():
    """Main function to split enhanced_admin_dashboard.py."""
    logger.info("Starting to split enhanced_admin_dashboard.py into modular files...")
    
    # Read enhanced_admin_dashboard.py
    with open('enhanced_admin_dashboard.py', 'r') as f:
        content = f.read()
    
    # Extract imports
    imports = extract_imports(content)
    
    # Extract function blocks
    functions = extract_function_blocks(content)
    logger.info(f"Extracted {len(functions)} functions from enhanced_admin_dashboard.py")
    
    # Categorize functions
    categories = categorize_functions(functions)
    
    # Create module files
    create_module_files(categories, imports)
    
    # Create proxy module
    create_proxy_module()
    
    logger.info("Finished splitting enhanced_admin_dashboard.py into modular files.")
    logger.info("To use the new structure, rename enhanced_admin_dashboard.py.new to enhanced_admin_dashboard.py")

if __name__ == '__main__':
    main()