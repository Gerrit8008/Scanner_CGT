#!/usr/bin/env python3
"""
Split client_db.py into smaller, modular files while maintaining functionality.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the directory structure
DB_MODULES_DIR = 'db_modules'
os.makedirs(DB_MODULES_DIR, exist_ok=True)

# Create __init__.py in db_modules directory
with open(os.path.join(DB_MODULES_DIR, '__init__.py'), 'w') as f:
    f.write('# Database modules package\n')

def extract_function_blocks(content):
    """Extract function definitions with their docstrings from content."""
    # Pattern to match function definitions with decorators
    func_pattern = r'(@\w+\([^)]*\)\s+)*def\s+(\w+)\s*\([^)]*\):'
    
    # Find all function definitions
    matches = list(re.finditer(func_pattern, content))
    
    functions = []
    for i, match in enumerate(matches):
        func_name = match.group(2)
        start_pos = match.start()
        
        # Look for decorators before the function
        decorator_start = start_pos
        line_start = content.rfind('\n', 0, start_pos) + 1
        while line_start > 0:
            line = content[line_start:decorator_start].strip()
            if line.startswith('@'):
                decorator_start = line_start
                line_start = content.rfind('\n', 0, line_start - 1) + 1
            else:
                break
        
        # Find end of the function (either the next function or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the function with its decorators
        func_block = content[decorator_start:end_pos].strip()
        functions.append((func_name, func_block))
    
    return functions

def categorize_functions(functions):
    """Categorize functions into modules based on their names and functionality."""
    categories = {
        'core': [],
        'auth': [],
        'client': [],
        'scanner': [],
        'scan_results': [],
        'dashboard': [],
        'utilities': [],
        'admin': [],
        'customization': [],
    }
    
    for func_name, func_block in functions:
        if func_name.startswith('get_db') or func_name == 'with_transaction' or func_name.startswith('initialize'):
            categories['core'].append((func_name, func_block))
        elif 'auth' in func_name or 'login' in func_name or 'password' in func_name or 'session' in func_name or 'user' in func_name:
            categories['auth'].append((func_name, func_block))
        elif 'client' in func_name and not 'scanner' in func_name and not 'scan' in func_name:
            categories['client'].append((func_name, func_block))
        elif 'scanner' in func_name and not 'scan_' in func_name and not 'result' in func_name:
            categories['scanner'].append((func_name, func_block))
        elif 'scan' in func_name and ('result' in func_name or 'history' in func_name or 'report' in func_name):
            categories['scan_results'].append((func_name, func_block))
        elif 'dashboard' in func_name or 'statistic' in func_name or 'chart' in func_name or 'summary' in func_name:
            categories['dashboard'].append((func_name, func_block))
        elif 'admin' in func_name:
            categories['admin'].append((func_name, func_block))
        elif 'customize' in func_name or 'style' in func_name or 'color' in func_name or 'theme' in func_name or 'font' in func_name:
            categories['customization'].append((func_name, func_block))
        else:
            categories['utilities'].append((func_name, func_block))
    
    return categories

def create_module_files(categories, imports, schema):
    """Create module files for each category."""
    for category, functions in categories.items():
        if not functions:
            logger.info(f"Skipping empty category: {category}")
            continue
        
        # Generate file content
        file_content = f'''"""
Database module for {category} functionality.
Generated from client_db.py
"""

{imports}

{schema if category == 'core' else ''}

'''
        
        # Add functions
        for _, func_block in functions:
            file_content += func_block + "\n\n"
        
        # Write to file
        file_path = os.path.join(DB_MODULES_DIR, f"{category}.py")
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        logger.info(f"Created {file_path} with {len(functions)} functions")

def create_proxy_module():
    """Create a proxy client_db.py that imports from modular files."""
    with open('client_db.py.new', 'w') as f:
        f.write('''"""
Database utility functions for CybrScan.
This file imports and re-exports functions from modular database files.
"""

import os
import sqlite3
import json
import logging
import traceback
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
import functools
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scanner_platform.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import all functions from modular files
from db_modules.core import *
from db_modules.auth import *
from db_modules.client import *
from db_modules.scanner import *
from db_modules.scan_results import *
from db_modules.dashboard import *
from db_modules.admin import *
from db_modules.customization import *
from db_modules.utilities import *

# Define database path
CLIENT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db')
''')
    
    logger.info("Created client_db.py.new proxy file")

def main():
    """Main function to split client_db.py."""
    logger.info("Starting to split client_db.py into modular files...")
    
    # Read client_db.py
    with open('client_db.py', 'r') as f:
        content = f.read()
    
    # Extract imports and schema
    imports_pattern = r'import.*?(?=\n\n# Define database path)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)
    imports = imports_match.group(0) if imports_match else ''
    
    schema_pattern = r'# Create the schema string for initialization.*?(?=\n\n# Database initialization function)'
    schema_match = re.search(schema_pattern, content, re.DOTALL)
    schema = schema_match.group(0) if schema_match else ''
    
    # Extract function blocks
    functions = extract_function_blocks(content)
    logger.info(f"Extracted {len(functions)} functions from client_db.py")
    
    # Categorize functions
    categories = categorize_functions(functions)
    
    # Create module files
    create_module_files(categories, imports, schema)
    
    # Create proxy module
    create_proxy_module()
    
    logger.info("Finished splitting client_db.py into modular files.")
    logger.info("To use the new structure, rename client_db.py.new to client_db.py")

if __name__ == '__main__':
    main()