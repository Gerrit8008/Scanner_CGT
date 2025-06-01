#!/usr/bin/env python3
"""
Update Scanner Limits

This script adds subscription limit checks to scanner creation and viewing.
It updates the scanner templates to show subscription limits.
"""

import os
import re
import logging
import sqlite3
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a connection to the database"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def update_database_schema():
    """Update the database schema to support scanner limits"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the scan_limit and scanner_limit columns exist
        cursor.execute("PRAGMA table_info(clients)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'scan_limit' not in columns:
            logger.info("Adding scan_limit column to clients table")
            cursor.execute("ALTER TABLE clients ADD COLUMN scan_limit INTEGER DEFAULT 10")
        
        if 'scanner_limit' not in columns:
            logger.info("Adding scanner_limit column to clients table")
            cursor.execute("ALTER TABLE clients ADD COLUMN scanner_limit INTEGER DEFAULT 1")
        
        conn.commit()
        
        # Update existing clients with proper limits based on their subscription level
        cursor.execute("SELECT id, subscription_level FROM clients")
        clients = cursor.fetchall()
        
        for client in clients:
            client_id = client['id']
            level = client['subscription_level']
            
            # Set limits based on subscription level
            if level == 'basic':
                scan_limit = 10
                scanner_limit = 1
            elif level == 'starter':
                scan_limit = 50
                scanner_limit = 1
            elif level == 'professional':
                scan_limit = 500
                scanner_limit = 3
            elif level == 'enterprise':
                scan_limit = 1000
                scanner_limit = 10
            else:
                # Default to basic
                scan_limit = 10
                scanner_limit = 1
            
            # Update client limits
            cursor.execute("""
                UPDATE clients
                SET scan_limit = ?, scanner_limit = ?
                WHERE id = ?
            """, (scan_limit, scanner_limit, client_id))
        
        conn.commit()
        conn.close()
        
        logger.info("Database schema updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating database schema: {e}")
        return False

def update_scanner_create_template():
    """Update the scanner-create.html template to show subscription limits"""
    try:
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     'templates/client/scanner-create.html')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            logger.error(f"Scanner create template not found: {template_path}")
            return False
        
        # Create a backup of the original file
        backup_path = f"{template_path}.bak"
        with open(template_path, 'r') as f:
            original_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(original_content)
            
        logger.info(f"Created backup at {backup_path}")
        
        # Add subscription limit warning at the top of the form
        form_start_pattern = r'<h2>Create New Scanner</h2>'
        subscription_warning = """<h2>Create New Scanner</h2>
                {% if scanner_count >= scanner_limit %}
                <div class="alert alert-warning mb-4">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <strong>Subscription limit reached:</strong> Your {{ subscription_level|capitalize }} plan allows {{ scanner_limit }} scanner{{ "s" if scanner_limit != 1 else "" }}.
                    <a href="/client/subscription/upgrade" class="alert-link">Upgrade your plan</a> to create more scanners.
                </div>
                {% else %}
                <div class="alert alert-info mb-4">
                    <i class="bi bi-info-circle-fill me-2"></i>
                    You have created {{ scanner_count }} of {{ scanner_limit }} available scanners with your {{ subscription_level|capitalize }} plan.
                </div>
                {% endif %}"""
        
        updated_content = original_content.replace(form_start_pattern, subscription_warning)
        
        # Disable form submission if limit reached
        form_tag_pattern = r'<form method="post" action="/client/scanners/create">'
        form_tag_replacement = """<form method="post" action="/client/scanners/create" {% if scanner_count >= scanner_limit %}onsubmit="alert('Subscription limit reached. Please upgrade your plan to create more scanners.'); return false;"{% endif %}>"""
        
        updated_content = updated_content.replace(form_tag_pattern, form_tag_replacement)
        
        # Update the submit button
        submit_button_pattern = r'<button type="submit" class="btn btn-primary">Create Scanner</button>'
        submit_button_replacement = """<button type="submit" class="btn btn-primary" {% if scanner_count >= scanner_limit %}disabled{% endif %}>
                                    {% if scanner_count >= scanner_limit %}Limit Reached{% else %}Create Scanner{% endif %}
                                </button>
                                {% if scanner_count >= scanner_limit %}
                                <a href="/client/subscription/upgrade" class="btn btn-success ms-2">Upgrade Plan</a>
                                {% endif %}"""
        
        updated_content = updated_content.replace(submit_button_pattern, submit_button_replacement)
        
        # Write the updated content back to the file
        with open(template_path, 'w') as f:
            f.write(updated_content)
            
        logger.info("Updated scanner create template successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating scanner create template: {e}")
        
        # Restore the backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                original_content = f.read()
            
            with open(template_path, 'w') as f:
                f.write(original_content)
                
            logger.info("Restored backup after error")
            
        return False

def update_scanners_list_template():
    """Update the scanners.html template to show subscription limits"""
    try:
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     'templates/client/scanners.html')
        
        # Check if the file exists
        if not os.path.exists(template_path):
            logger.error(f"Scanners list template not found: {template_path}")
            return False
        
        # Create a backup of the original file
        backup_path = f"{template_path}.bak"
        with open(template_path, 'r') as f:
            original_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(original_content)
            
        logger.info(f"Created backup at {backup_path}")
        
        # Add subscription limit warning above the scanner list
        pattern = r'<h2>My Scanners</h2>'
        replacement = """<h2>My Scanners</h2>
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <span class="badge bg-info">{{ subscription_level|capitalize }} Plan</span>
                        <span class="badge bg-secondary">{{ scanners|length }} / {{ scanner_limit }} Scanners</span>
                        <span class="badge bg-secondary">{{ scan_count }} / {{ scan_limit }} Scans/month</span>
                    </div>
                    <a href="/client/subscription/upgrade" class="btn btn-sm btn-outline-primary">Upgrade Plan</a>
                </div>"""
        
        updated_content = original_content.replace(pattern, replacement)
        
        # Update the create scanner button
        button_pattern = r'<a href="/client/scanners/create" class="btn btn-primary">'
        button_replacement = """<a href="/client/scanners/create" class="btn btn-primary {% if scanners|length >= scanner_limit %}disabled{% endif %}">
                                {% if scanners|length >= scanner_limit %}Scanner Limit Reached{% else %}Create New Scanner{% endif %}
                            </a>"""
        
        updated_content = updated_content.replace(button_pattern, button_replacement)
        
        # Write the updated content back to the file
        with open(template_path, 'w') as f:
            f.write(updated_content)
            
        logger.info("Updated scanners list template successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating scanners list template: {e}")
        
        # Restore the backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                original_content = f.read()
            
            with open(template_path, 'w') as f:
                f.write(original_content)
                
            logger.info("Restored backup after error")
            
        return False

def update_scanner_routes():
    """Update the scanner routes to check subscription limits"""
    try:
        # Find scanner routes files (could be scanner.py, scanner_routes.py, etc.)
        scanner_routes_files = []
        for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            if filename.endswith('.py') and ('scanner' in filename.lower() or 'scan' in filename.lower()):
                scanner_routes_files.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
        
        logger.info(f"Found {len(scanner_routes_files)} potential scanner route files")
        
        # Add limit checking to each file
        for file_path in scanner_routes_files:
            # Check if the file contains scanner creation routes
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Only modify files that have scanner creation routes
            if '/scanner' in content and 'create' in content and 'post' in content.lower():
                # Create a backup of the original file
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w') as f:
                    f.write(content)
                    
                logger.info(f"Created backup at {backup_path}")
                
                # Import section at the top of the file
                import_section = """# Import subscription limit check
from subscription_constants import get_subscription_limit
"""
                # Add import if not already present
                if 'from subscription_constants import' not in content:
                    # Find the end of the import section
                    import_end = content.find('\n\n', content.find('import'))
                    if import_end > 0:
                        updated_content = content[:import_end] + '\n' + import_section + content[import_end:]
                    else:
                        updated_content = import_section + content
                else:
                    updated_content = content
                
                # Add subscription limit check function
                if 'def check_scanner_limit' not in updated_content:
                    limit_check_function = """
def check_scanner_limit(client_id, conn=None, cursor=None):
    """Check if a client has reached their scanner limit"""
    # Create connection if not provided
    close_conn = False
    if conn is None or cursor is None:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True
    
    try:
        # Get client subscription level and scanner limit
        cursor.execute(\"\"\"
            SELECT id, subscription_level, scanner_limit
            FROM clients 
            WHERE id = ?
        \"\"\", (client_id,))
        
        client = cursor.fetchone()
        if not client:
            return (False, 0, 0, 0)
        
        # Get subscription level and scanner limit
        subscription_level = client['subscription_level'] if hasattr(client, 'keys') else client[1]
        scanner_limit = client['scanner_limit'] if hasattr(client, 'keys') else client[2]
        
        if scanner_limit is None:
            # Default limits based on subscription level
            if subscription_level == 'basic':
                scanner_limit = 1
            elif subscription_level == 'starter':
                scanner_limit = 1
            elif subscription_level == 'professional':
                scanner_limit = 3
            elif subscription_level == 'enterprise':
                scanner_limit = 10
            else:
                scanner_limit = 1  # Default for unknown levels
        
        # Count active scanners
        cursor.execute(\"\"\"
            SELECT COUNT(*) as scanner_count
            FROM scanners
            WHERE client_id = ? AND status != 'deleted'
        \"\"\", (client_id,))
        
        scanner_count_row = cursor.fetchone()
        scanner_count = scanner_count_row[0] if scanner_count_row else 0
        
        # Check if limit is reached
        has_reached_limit = scanner_count >= scanner_limit
        remaining = max(0, scanner_limit - scanner_count)
        
        if close_conn:
            conn.close()
            
        return (has_reached_limit, scanner_limit, scanner_count, remaining)
    except Exception as e:
        # Log error but don't block scanner creation if checking fails
        print(f"Error checking scanner limit: {e}")
        if close_conn:
            conn.close()
        return (False, 0, 0, 0)
"""
                    # Add the function after the imports
                    function_pos = updated_content.find('\n\n', updated_content.find('import'))
                    if function_pos > 0:
                        updated_content = updated_content[:function_pos] + '\n' + limit_check_function + updated_content[function_pos:]
                    else:
                        updated_content = updated_content + '\n' + limit_check_function
                
                # Find scanner creation routes and add limit check
                route_patterns = [
                    r'@.*route\([\'"].*scanners?.*create[\'"]', 
                    r'@.*route\([\'"].*scanners?/new[\'"]',
                    r'def create_scanner'
                ]
                
                for pattern in route_patterns:
                    matches = list(re.finditer(pattern, updated_content))
                    for match in matches:
                        # Find the beginning of the function body
                        function_body_start = updated_content.find(':', match.start())
                        if function_body_start > 0:
                            # Find the indentation level
                            next_line_start = updated_content.find('\n', function_body_start) + 1
                            next_line_end = updated_content.find('\n', next_line_start)
                            if next_line_start > 0 and next_line_end > 0:
                                indentation = ''
                                for char in updated_content[next_line_start:next_line_end]:
                                    if char in (' ', '\t'):
                                        indentation += char
                                    else:
                                        break
                                
                                # Add limit check at the beginning of the function body
                                limit_check_code = f"""
{indentation}# Check if client has reached their scanner limit
{indentation}client_id = request.form.get('client_id') or session.get('client_id')
{indentation}if client_id:
{indentation}    has_reached_limit, scanner_limit, scanner_count, remaining = check_scanner_limit(client_id)
{indentation}    if has_reached_limit:
{indentation}        flash('You have reached your scanner limit. Please upgrade your subscription to create more scanners.', 'warning')
{indentation}        return redirect(url_for('client.scanners'))
"""
                                
                                # Insert the limit check code
                                insert_pos = next_line_start
                                updated_content = updated_content[:insert_pos] + limit_check_code + updated_content[insert_pos:]
                
                # Write the updated content back to the file
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                    
                logger.info(f"Updated scanner routes in {file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating scanner routes: {e}")
        return False

def update_client_dashboard_route():
    """Update the client dashboard route to pass subscription limits to templates"""
    try:
        # Find client route files
        client_routes_files = []
        for filename in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            if filename.endswith('.py') and 'client' in filename.lower():
                client_routes_files.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
        
        logger.info(f"Found {len(client_routes_files)} potential client route files")
        
        # Add subscription limits to each file
        for file_path in client_routes_files:
            # Check if the file contains client dashboard routes
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Only modify files that have client dashboard routes
            if '/client/dashboard' in content or '/client/scanners' in content:
                # Create a backup of the original file
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w') as f:
                    f.write(content)
                    
                logger.info(f"Created backup at {backup_path}")
                
                # Import section at the top of the file
                import_section = """# Import subscription limit functions
from subscription_constants import get_subscription_limit
"""
                # Add import if not already present
                if 'from subscription_constants import' not in content:
                    # Find the end of the import section
                    import_end = content.find('\n\n', content.find('import'))
                    if import_end > 0:
                        updated_content = content[:import_end] + '\n' + import_section + content[import_end:]
                    else:
                        updated_content = import_section + content
                else:
                    updated_content = content
                
                # Find route handlers for client dashboard and scanners page
                route_patterns = [
                    r'@.*route\([\'"].*client/dashboard[\'"]', 
                    r'@.*route\([\'"].*client/scanners[\'"]',
                    r'def client_dashboard',
                    r'def scanners'
                ]
                
                for pattern in route_patterns:
                    matches = list(re.finditer(pattern, updated_content))
                    for match in matches:
                        # Find the render_template call
                        render_pos = updated_content.find('render_template', match.start())
                        if render_pos > 0:
                            # Find the end of the render_template call
                            render_end = updated_content.find(')', render_pos)
                            if render_end > 0:
                                # Add subscription limits to the render_template call
                                subscription_limits_code = """
                # Get subscription limits
                subscription_level = client.get('subscription_level', 'basic')
                scanner_limit = client.get('scanner_limit', 1)
                if scanner_limit is None:
                    scanner_limit = get_subscription_limit(subscription_level, 'scanners')
                
                scan_limit = client.get('scan_limit', 10)
                if scan_limit is None:
                    scan_limit = get_subscription_limit(subscription_level, 'scans')
                
                # Add subscription limits to template variables
                """
                                
                                # Get the indentation level
                                line_start = updated_content.rfind('\n', 0, render_pos) + 1
                                indentation = ''
                                for char in updated_content[line_start:render_pos]:
                                    if char in (' ', '\t'):
                                        indentation += char
                                    else:
                                        break
                                
                                # Format the code with proper indentation
                                subscription_limits_code = '\n'.join([indentation + line.strip() for line in subscription_limits_code.split('\n') if line.strip()])
                                
                                # Add the subscription limits code before the render_template call
                                updated_content = updated_content[:render_pos] + subscription_limits_code + '\n' + indentation + updated_content[render_pos:]
                                
                                # Find the closing parenthesis of the render_template call
                                render_end = updated_content.find(')', render_pos)
                                if render_end > 0 and updated_content[render_end-1] != ',':
                                    # Add subscription limits to the template variables
                                    subscription_vars = ",\n" + indentation + "    subscription_level=subscription_level,\n" + indentation + "    scanner_limit=scanner_limit,\n" + indentation + "    scan_limit=scan_limit"
                                    updated_content = updated_content[:render_end] + subscription_vars + updated_content[render_end:]
                
                # Write the updated content back to the file
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                    
                logger.info(f"Updated client dashboard route in {file_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error updating client dashboard route: {e}")
        return False

def main():
    """Main function to update scanner limits"""
    logger.info("Starting scanner limits update")
    
    # Update database schema
    if not update_database_schema():
        logger.error("Failed to update database schema, continuing anyway")
    
    # Update scanner create template
    if not update_scanner_create_template():
        logger.error("Failed to update scanner create template, continuing anyway")
    
    # Update scanners list template
    if not update_scanners_list_template():
        logger.error("Failed to update scanners list template, continuing anyway")
    
    # Update scanner routes
    if not update_scanner_routes():
        logger.error("Failed to update scanner routes, continuing anyway")
    
    # Update client dashboard route
    if not update_client_dashboard_route():
        logger.error("Failed to update client dashboard route, continuing anyway")
    
    logger.info("Scanner limits update completed")

if __name__ == "__main__":
    main()
    print("✅ Scanner limits updated successfully")