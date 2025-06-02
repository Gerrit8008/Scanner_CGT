#!/usr/bin/env python3
"""
Split scan.py into smaller, modular files while maintaining functionality.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the directory structure
SCAN_MODULES_DIR = 'scan_modules'
os.makedirs(SCAN_MODULES_DIR, exist_ok=True)

# Create __init__.py in scan_modules directory
with open(os.path.join(SCAN_MODULES_DIR, '__init__.py'), 'w') as f:
    f.write('# Scan modules package\n')

def extract_function_blocks(content):
    """Extract function definitions with their docstrings from content."""
    # Pattern to match function definitions
    func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    
    # Find all function definitions
    matches = list(re.finditer(func_pattern, content))
    
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

def extract_constants(content):
    """Extract constant definitions from content."""
    # Look for constants section
    constants_pattern = r'# Constants for severity levels and warnings(.*?)# -+'
    constants_match = re.search(constants_pattern, content, re.DOTALL)
    
    if constants_match:
        return constants_match.group(1).strip()
    return ""

def categorize_functions(functions):
    """Categorize functions into modules based on their names and functionality."""
    categories = {
        'network': [],
        'web': [],
        'dns': [],
        'ssl': [],
        'industry': [],
        'vulnerability': [],
        'reporting': [],
        'utilities': [],
    }
    
    for func_name, func_block in functions:
        if 'port' in func_name or 'gateway' in func_name or 'network' in func_name or 'ip' in func_name:
            categories['network'].append((func_name, func_block))
        elif 'web' in func_name or 'http' in func_name or 'cms' in func_name or 'cookie' in func_name or 'header' in func_name:
            categories['web'].append((func_name, func_block))
        elif 'dns' in func_name or 'domain' in func_name or 'spf' in func_name or 'dmarc' in func_name or 'dkim' in func_name:
            categories['dns'].append((func_name, func_block))
        elif 'ssl' in func_name or 'tls' in func_name or 'certificate' in func_name:
            categories['ssl'].append((func_name, func_block))
        elif 'industry' in func_name or 'sector' in func_name or 'company' in func_name:
            categories['industry'].append((func_name, func_block))
        elif 'vulnerability' in func_name or 'exploit' in func_name or 'cve' in func_name or 'risk' in func_name:
            categories['vulnerability'].append((func_name, func_block))
        elif 'report' in func_name or 'result' in func_name or 'format' in func_name or 'generate' in func_name:
            categories['reporting'].append((func_name, func_block))
        else:
            categories['utilities'].append((func_name, func_block))
    
    return categories

def create_module_files(categories, imports, constants):
    """Create module files for each category."""
    for category, functions in categories.items():
        if not functions:
            logger.info(f"Skipping empty category: {category}")
            continue
        
        # Generate file content
        file_content = f'''"""
Scan module for {category} functionality.
Generated from scan.py
"""

{imports}

{constants if category == 'utilities' else ''}

'''
        
        # Add functions
        for _, func_block in functions:
            file_content += func_block + "\n\n"
        
        # Write to file
        file_path = os.path.join(SCAN_MODULES_DIR, f"{category}.py")
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        logger.info(f"Created {file_path} with {len(functions)} functions")

def create_proxy_module():
    """Create a proxy scan.py that imports from modular files."""
    with open('scan.py.new', 'w') as f:
        f.write('''"""
Security scanning functionality for CybrScan.
This file imports and re-exports functions from modular scan files.
"""

import os
import platform
import socket
import re
import uuid
import urllib.parse
from datetime import datetime
import random
import ipaddress
import json
import logging
import ssl
import requests
from bs4 import BeautifulSoup
import dns.resolver

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Import constants from utilities module
from scan_modules.utilities import (
    SEVERITY, 
    SEVERITY_ICONS,
    GATEWAY_PORT_WARNINGS
)

# Import all functions from modular files
from scan_modules.network import *
from scan_modules.web import *
from scan_modules.dns import *
from scan_modules.ssl import *
from scan_modules.industry import *
from scan_modules.vulnerability import *
from scan_modules.reporting import *
from scan_modules.utilities import *
''')
    
    logger.info("Created scan.py.new proxy file")

def extract_imports(content):
    """Extract import statements from content."""
    imports_pattern = r'import.*?(?=# Constants for severity|# -+)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)
    
    if imports_match:
        return imports_match.group(0).strip()
    return ""

def main():
    """Main function to split scan.py."""
    logger.info("Starting to split scan.py into modular files...")
    
    # Read scan.py
    with open('scan.py', 'r') as f:
        content = f.read()
    
    # Extract imports
    imports = extract_imports(content)
    
    # Extract constants
    constants = extract_constants(content)
    
    # Extract function blocks
    functions = extract_function_blocks(content)
    logger.info(f"Extracted {len(functions)} functions from scan.py")
    
    # Categorize functions
    categories = categorize_functions(functions)
    
    # Create module files
    create_module_files(categories, imports, constants)
    
    # Create proxy module
    create_proxy_module()
    
    logger.info("Finished splitting scan.py into modular files.")
    logger.info("To use the new structure, rename scan.py.new to scan.py")

if __name__ == '__main__':
    main()