#!/usr/bin/env python3
"""
Split client.py into smaller, modular files while maintaining functionality.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the directory structure
CLIENT_MODULES_DIR = 'client_modules'
os.makedirs(CLIENT_MODULES_DIR, exist_ok=True)

# Create __init__.py in client_modules directory
with open(os.path.join(CLIENT_MODULES_DIR, '__init__.py'), 'w') as f:
    f.write('# Client modules package\n')

def extract_route_blocks(content):
    """Extract route definitions from content."""
    # Pattern to match route definitions
    route_pattern = r'@client_bp\.route\([^\)]+\)(?:\s+@[^\)]+\))*\s+def\s+(\w+)\s*\([^)]*\):'
    
    # Find all route definitions
    matches = list(re.finditer(route_pattern, content, re.DOTALL))
    
    routes = []
    for i, match in enumerate(matches):
        route_name = match.group(1)
        start_pos = match.start()
        
        # Find end of the route (either the next route or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the route
        route_block = content[start_pos:end_pos].strip()
        routes.append((route_name, route_block))
    
    return routes

def extract_helper_functions(content, route_blocks):
    """Extract helper functions that are not routes."""
    # Pattern to match function definitions
    func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    
    # Find all function definitions
    matches = list(re.finditer(func_pattern, content, re.DOTALL))
    
    helper_functions = []
    for match in matches:
        func_name = match.group(1)
        start_pos = match.start()
        
        # Skip if this is a route function
        is_route = False
        for route_name, route_block in route_blocks:
            if func_name == route_name:
                is_route = True
                break
        
        if is_route:
            continue
        
        # Find end of the function (can be complex, simplified approach)
        # Look for the next def that's not indented
        next_def_pos = content.find('\ndef ', start_pos + 1)
        if next_def_pos == -1:
            next_def_pos = len(content)
        
        # Extract the function
        func_block = content[start_pos:next_def_pos].strip()
        helper_functions.append((func_name, func_block))
    
    return helper_functions

def categorize_routes(routes):
    """Categorize routes into modules based on their names and functionality."""
    categories = {
        'dashboard': [],
        'scanners': [],
        'reports': [],
        'settings': [],
        'profile': [],
        'misc': [],
    }
    
    for route_name, route_block in routes:
        if 'dashboard' in route_name:
            categories['dashboard'].append((route_name, route_block))
        elif 'scanner' in route_name or 'scan' in route_name and not 'report' in route_name:
            categories['scanners'].append((route_name, route_block))
        elif 'report' in route_name or 'result' in route_name:
            categories['reports'].append((route_name, route_block))
        elif 'setting' in route_name or 'config' in route_name or 'preference' in route_name:
            categories['settings'].append((route_name, route_block))
        elif 'profile' in route_name or 'account' in route_name or 'user' in route_name:
            categories['profile'].append((route_name, route_block))
        else:
            categories['misc'].append((route_name, route_block))
    
    return categories

def create_module_files(categories, helpers, imports, blueprint_def):
    """Create module files for each category."""
    # Create utils.py with helper functions
    utils_content = f'''"""
Client utility functions.
Generated from client.py
"""

{imports}

'''
    
    for _, func_block in helpers:
        utils_content += func_block + "\n\n"
    
    utils_path = os.path.join(CLIENT_MODULES_DIR, "utils.py")
    with open(utils_path, 'w') as f:
        f.write(utils_content)
    
    logger.info(f"Created {utils_path} with {len(helpers)} helper functions")
    
    # Create module files for each category
    for category, routes in categories.items():
        if not routes:
            logger.info(f"Skipping empty category: {category}")
            continue
        
        # Generate file content
        file_content = f'''"""
Client routes for {category} functionality.
Generated from client.py
"""

{imports}

from client_modules.utils import *

{blueprint_def}

'''
        
        # Add routes
        for _, route_block in routes:
            file_content += route_block + "\n\n"
        
        # Write to file
        file_path = os.path.join(CLIENT_MODULES_DIR, f"{category}.py")
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        logger.info(f"Created {file_path} with {len(routes)} routes")

def create_proxy_module():
    """Create a proxy client.py that imports from modular files."""
    with open('client.py.new', 'w') as f:
        f.write('''"""
Client blueprint and routes for CybrScan.
This file imports and re-exports routes from modular client files.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
import logging
import json
import re
import time
from datetime import datetime
from functools import wraps

# Import database functions
from client_db import (
    verify_session,
    get_client_by_user_id, 
    get_deployed_scanners_by_client_id,
    get_scan_history_by_client_id,
    get_scanner_by_id,
    update_scanner_config,
    regenerate_scanner_api_key,
    log_scan,
    get_scan_history,
    get_scanner_stats,
    update_client,
    get_client_statistics,
    get_recent_activities,
    get_available_scanners_for_client,
    get_client_dashboard_data,
    format_scan_results_for_client,
    register_client,
    get_scan_reports_for_client,
    get_scan_statistics_for_client,
    get_db_connection
)

# Create client blueprint
client_bp = Blueprint('client', __name__, url_prefix='/client')

# Import utilities
from client_modules.utils import *

# Import all routes from modular files
from client_modules.dashboard import *
from client_modules.scanners import *
from client_modules.reports import *
from client_modules.settings import *
from client_modules.profile import *
from client_modules.misc import *
''')
    
    logger.info("Created client.py.new proxy file")

def extract_imports_and_blueprint(content):
    """Extract import statements and blueprint definition."""
    # Extract imports
    imports_pattern = r'from flask.*?(?=def\s+\w+)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)
    imports = imports_match.group(0).strip() if imports_match else ''
    
    # Extract blueprint definition
    blueprint_pattern = r'client_bp = Blueprint.*?\)'
    blueprint_match = re.search(blueprint_pattern, content)
    blueprint_def = blueprint_match.group(0) if blueprint_match else 'client_bp = Blueprint("client", __name__, url_prefix="/client")'
    
    return imports, blueprint_def

def main():
    """Main function to split client.py."""
    logger.info("Starting to split client.py into modular files...")
    
    # Read client.py
    with open('client.py', 'r') as f:
        content = f.read()
    
    # Extract imports and blueprint definition
    imports, blueprint_def = extract_imports_and_blueprint(content)
    
    # Extract route blocks
    routes = extract_route_blocks(content)
    logger.info(f"Extracted {len(routes)} routes from client.py")
    
    # Extract helper functions
    helpers = extract_helper_functions(content, routes)
    logger.info(f"Extracted {len(helpers)} helper functions from client.py")
    
    # Categorize routes
    categories = categorize_routes(routes)
    
    # Create module files
    create_module_files(categories, helpers, imports, blueprint_def)
    
    # Create proxy module
    create_proxy_module()
    
    logger.info("Finished splitting client.py into modular files.")
    logger.info("To use the new structure, rename client.py.new to client.py")

if __name__ == '__main__':
    main()