#!/usr/bin/env python3
"""
Split enhanced_scan.py into smaller, modular files while maintaining functionality.
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the directory structure
ENHANCED_SCAN_MODULES_DIR = 'enhanced_scan_modules'
os.makedirs(ENHANCED_SCAN_MODULES_DIR, exist_ok=True)

# Create __init__.py in enhanced_scan_modules directory
with open(os.path.join(ENHANCED_SCAN_MODULES_DIR, '__init__.py'), 'w') as f:
    f.write('# Enhanced scan modules package\n')

def extract_classes(content):
    """Extract class definitions from content."""
    # Pattern to match class definitions
    class_pattern = r'class\s+(\w+)\s*\(.*\):'
    
    # Find all class definitions
    matches = list(re.finditer(class_pattern, content, re.MULTILINE))
    
    classes = []
    for i, match in enumerate(matches):
        class_name = match.group(1)
        start_pos = match.start()
        
        # Find end of the class (either the next class or end of file)
        if i < len(matches) - 1:
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract the class
        class_block = content[start_pos:end_pos].strip()
        classes.append((class_name, class_block))
    
    return classes

def extract_function_blocks(content, class_blocks):
    """Extract function definitions that are not part of classes."""
    # Pattern to match function definitions
    func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
    
    # Find all function definitions
    matches = list(re.finditer(func_pattern, content, re.MULTILINE))
    
    functions = []
    for match in matches:
        func_name = match.group(1)
        start_pos = match.start()
        
        # Skip if this function is part of a class
        is_in_class = False
        for _, class_block in class_blocks:
            if func_name in class_block and match.group(0) in class_block:
                is_in_class = True
                break
        
        if is_in_class:
            continue
        
        # Find end of the function (simplified approach)
        end_pos = len(content)
        for next_match in matches:
            if next_match.start() > start_pos:
                end_pos = next_match.start()
                break
        
        # Extract the function
        func_block = content[start_pos:end_pos].strip()
        functions.append((func_name, func_block))
    
    return functions

def categorize_scan_components(classes, functions):
    """Categorize classes and functions into modules."""
    categories = {
        'progress_tracking': [],  # Progress tracking and real-time updates
        'network_scan': [],  # Network scanning components
        'web_scan': [],  # Web application scanning
        'dns_scan': [],  # DNS and domain scanning
        'ssl_scan': [],  # SSL/TLS certificate scanning
        'vulnerability_scan': [],  # Vulnerability detection
        'results': [],  # Result processing and formatting
        'utils': [],  # Utility functions
    }
    
    # Categorize classes
    for class_name, class_block in classes:
        if 'Progress' in class_name or 'Tracker' in class_name:
            categories['progress_tracking'].append(('class', class_name, class_block))
        elif 'Network' in class_name or 'Port' in class_name:
            categories['network_scan'].append(('class', class_name, class_block))
        elif 'Web' in class_name or 'Http' in class_name:
            categories['web_scan'].append(('class', class_name, class_block))
        elif 'DNS' in class_name or 'Domain' in class_name:
            categories['dns_scan'].append(('class', class_name, class_block))
        elif 'SSL' in class_name or 'Certificate' in class_name:
            categories['ssl_scan'].append(('class', class_name, class_block))
        elif 'Vulnerability' in class_name or 'CVE' in class_name:
            categories['vulnerability_scan'].append(('class', class_name, class_block))
        elif 'Result' in class_name or 'Report' in class_name:
            categories['results'].append(('class', class_name, class_block))
        else:
            categories['utils'].append(('class', class_name, class_block))
    
    # Categorize functions
    for func_name, func_block in functions:
        if 'progress' in func_name or 'track' in func_name or 'callback' in func_name:
            categories['progress_tracking'].append(('function', func_name, func_block))
        elif 'network' in func_name or 'port' in func_name or 'gateway' in func_name:
            categories['network_scan'].append(('function', func_name, func_block))
        elif 'web' in func_name or 'http' in func_name or 'crawl' in func_name:
            categories['web_scan'].append(('function', func_name, func_block))
        elif 'dns' in func_name or 'domain' in func_name:
            categories['dns_scan'].append(('function', func_name, func_block))
        elif 'ssl' in func_name or 'tls' in func_name or 'certificate' in func_name:
            categories['ssl_scan'].append(('function', func_name, func_block))
        elif 'vulnerability' in func_name or 'cve' in func_name or 'exploit' in func_name:
            categories['vulnerability_scan'].append(('function', func_name, func_block))
        elif 'result' in func_name or 'report' in func_name or 'format' in func_name:
            categories['results'].append(('function', func_name, func_block))
        else:
            categories['utils'].append(('function', func_name, func_block))
    
    return categories

def create_module_files(categories, imports):
    """Create module files for each category."""
    for category, components in categories.items():
        if not components:
            logger.info(f"Skipping empty category: {category}")
            continue
        
        # Generate file content
        file_content = f'''"""
Enhanced scan module for {category} functionality.
Generated from enhanced_scan.py
"""

{imports}

'''
        
        # Add classes and functions
        for comp_type, comp_name, comp_block in components:
            file_content += comp_block + "\n\n"
        
        # Write to file
        file_path = os.path.join(ENHANCED_SCAN_MODULES_DIR, f"{category}.py")
        with open(file_path, 'w') as f:
            f.write(file_content)
        
        logger.info(f"Created {file_path} with {len(components)} components")

def create_proxy_module():
    """Create a proxy enhanced_scan.py that imports from modular files."""
    with open('enhanced_scan.py.new', 'w') as f:
        f.write('''#!/usr/bin/env python3
"""
Enhanced CybrScan Security Scanner
Comprehensive implementation of all advertised scan types with real-time progress tracking
This file imports and re-exports functions from modular files.
"""

import os
import platform
import socket
import re
import uuid
import urllib.parse
import ssl
import requests
import dns.resolver
import subprocess
import time
import threading
import json
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import ipaddress
import concurrent.futures

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import all components from modular files
from enhanced_scan_modules.progress_tracking import *
from enhanced_scan_modules.network_scan import *
from enhanced_scan_modules.web_scan import *
from enhanced_scan_modules.dns_scan import *
from enhanced_scan_modules.ssl_scan import *
from enhanced_scan_modules.vulnerability_scan import *
from enhanced_scan_modules.results import *
from enhanced_scan_modules.utils import *
''')
    
    logger.info("Created enhanced_scan.py.new proxy file")

def extract_imports(content):
    """Extract import statements from content."""
    imports_pattern = r'import.*?(?=class|\ndef|\n\n)'
    imports_match = re.search(imports_pattern, content, re.DOTALL)
    
    if imports_match:
        return imports_match.group(0).strip()
    return ""

def main():
    """Main function to split enhanced_scan.py."""
    logger.info("Starting to split enhanced_scan.py into modular files...")
    
    # Read enhanced_scan.py
    with open('enhanced_scan.py', 'r') as f:
        content = f.read()
    
    # Extract imports
    imports = extract_imports(content)
    
    # Extract classes
    classes = extract_classes(content)
    logger.info(f"Extracted {len(classes)} classes from enhanced_scan.py")
    
    # Extract functions
    functions = extract_function_blocks(content, classes)
    logger.info(f"Extracted {len(functions)} functions from enhanced_scan.py")
    
    # Categorize components
    categories = categorize_scan_components(classes, functions)
    
    # Create module files
    create_module_files(categories, imports)
    
    # Create proxy module
    create_proxy_module()
    
    logger.info("Finished splitting enhanced_scan.py into modular files.")
    logger.info("To use the new structure, rename enhanced_scan.py.new to enhanced_scan.py")

if __name__ == '__main__':
    main()