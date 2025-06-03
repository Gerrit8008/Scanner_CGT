#!/usr/bin/env python3
"""
Fix scanner look and feel issues and ensure proper scanner and report routing
"""

import os
import logging
import sqlite3
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_scanner_integration():
    """Fix scanner integration and routing issues"""
    try:
        # Create routes directory if it doesn't exist
        routes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'routes')
        os.makedirs(routes_dir, exist_ok=True)
        
        # Fix scanner integration by linking app.py to proper scanner_routes.py
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        if os.path.exists(app_path):
            with open(app_path, 'r') as f:
                app_content = f.read()
            
            # Check if scanner_routes.py is imported and registered properly
            if 'from routes.scanner_routes import scanner_bp' not in app_content:
                updated_app_content = app_content
                
                # Add scanner import
                if 'from routes import' in app_content:
                    updated_app_content = updated_app_content.replace(
                        'from routes import',
                        'from routes import scanner_routes\nfrom routes.scanner_routes import scanner_bp'
                    )
                else:
                    # If no routes imports, add it after other imports
                    import_section_end = app_content.find('\n\n', app_content.find('import'))
                    if import_section_end > 0:
                        updated_app_content = (
                            app_content[:import_section_end] + 
                            '\nfrom routes.scanner_routes import scanner_bp' +
                            app_content[import_section_end:]
                        )
                
                # Register scanner blueprint if not already registered
                if 'app.register_blueprint(scanner_bp)' not in app_content:
                    blueprint_section = app_content.find('app.register_blueprint')
                    if blueprint_section > 0:
                        # Find the end of blueprint registrations
                        blueprint_section_end = app_content.find('\n\n', blueprint_section)
                        if blueprint_section_end > 0:
                            updated_app_content = (
                                updated_app_content[:blueprint_section_end] + 
                                '\napp.register_blueprint(scanner_bp)' +
                                updated_app_content[blueprint_section_end:]
                            )
                
                # Write updated app content if changes were made
                if updated_app_content != app_content:
                    with open(app_path, 'w') as f:
                        f.write(updated_app_content)
                    logger.info("Updated app.py to properly import and register scanner blueprint")
                else:
                    logger.info("Scanner blueprint is already imported and registered in app.py")
            else:
                logger.info("Scanner blueprint is already imported and registered in app.py")
        else:
            logger.warning(f"app.py not found at {app_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing scanner integration: {e}")
        return False

def fix_reports_integration():
    """Fix reports integration and routing issues"""
    try:
        # Ensure reports_routes.py is properly registered in app.py
        app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
        if os.path.exists(app_path):
            with open(app_path, 'r') as f:
                app_content = f.read()
            
            # Check if reports_bp is imported and registered properly
            if 'from reports_routes import reports_bp' not in app_content and 'from routes.reports_routes import reports_bp' not in app_content:
                updated_app_content = app_content
                
                # Add reports import
                if 'from routes import' in app_content:
                    updated_app_content = updated_app_content.replace(
                        'from routes import',
                        'from routes import reports_routes\nfrom reports_routes import reports_bp'
                    )
                else:
                    # If no routes imports, add it after other imports
                    import_section_end = app_content.find('\n\n', app_content.find('import'))
                    if import_section_end > 0:
                        updated_app_content = (
                            app_content[:import_section_end] + 
                            '\nfrom reports_routes import reports_bp' +
                            app_content[import_section_end:]
                        )
                
                # Register reports blueprint if not already registered
                if 'app.register_blueprint(reports_bp)' not in app_content:
                    blueprint_section = app_content.find('app.register_blueprint')
                    if blueprint_section > 0:
                        # Find the end of blueprint registrations
                        blueprint_section_end = app_content.find('\n\n', blueprint_section)
                        if blueprint_section_end > 0:
                            updated_app_content = (
                                updated_app_content[:blueprint_section_end] + 
                                '\napp.register_blueprint(reports_bp)' +
                                updated_app_content[blueprint_section_end:]
                            )
                
                # Write updated app content if changes were made
                if updated_app_content != app_content:
                    with open(app_path, 'w') as f:
                        f.write(updated_app_content)
                    logger.info("Updated app.py to properly import and register reports blueprint")
                else:
                    logger.info("Reports blueprint is already imported and registered in app.py")
            else:
                logger.info("Reports blueprint is already imported and registered in app.py")
        else:
            logger.warning(f"app.py not found at {app_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error fixing reports integration: {e}")
        return False

def create_missing_tables():
    """Create missing tables in client_scanner.db"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db')
        
        if not os.path.exists(db_path):
            logger.warning(f"Database not found at {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create scanners table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scanners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            scanner_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            domain TEXT,
            api_key TEXT,
            primary_color TEXT,
            secondary_color TEXT,
            button_color TEXT,
            logo_url TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            email_subject TEXT,
            email_intro TEXT,
            scan_types TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL,
            created_by INTEGER,
            updated_at TEXT,
            updated_by INTEGER
        )
        ''')
        
        # Create scan_history table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanner_id TEXT NOT NULL,
            scan_id TEXT UNIQUE NOT NULL,
            target_url TEXT,
            scan_type TEXT,
            status TEXT DEFAULT 'pending',
            results TEXT,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            client_id INTEGER,
            security_score INTEGER DEFAULT 0
        )
        ''')
        
        # Create customizations table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS customizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER UNIQUE NOT NULL,
            primary_color TEXT DEFAULT '#02054c',
            secondary_color TEXT DEFAULT '#35a310',
            button_color TEXT DEFAULT '#d96c33',
            font_family TEXT DEFAULT 'Roboto, sans-serif',
            color_style TEXT DEFAULT 'flat',
            logo_path TEXT,
            favicon_path TEXT,
            scanner_name TEXT,
            scanner_description TEXT,
            cta_button_text TEXT,
            company_tagline TEXT,
            email_subject TEXT,
            email_intro TEXT,
            support_email TEXT,
            custom_footer_text TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
        ''')
        
        # Create a sample scanner if there are no scanners
        cursor.execute('SELECT COUNT(*) FROM scanners')
        scanner_count = cursor.fetchone()[0]
        
        if scanner_count == 0:
            # Create a default scanner
            cursor.execute('''
            INSERT INTO scanners (
                client_id, scanner_id, name, description, api_key, 
                primary_color, secondary_color, button_color, 
                scan_types, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                1,
                'scanner_' + datetime.now().strftime('%Y%m%d%H%M%S'),
                'Security Scanner',
                'Comprehensive security assessment scanner',
                'api_' + os.urandom(16).hex(),
                '#02054c',
                '#35a310',
                '#d96c33',
                'network,web,ssl,dns',
                datetime.now().isoformat()
            ))
            logger.info("Created default scanner")
        
        conn.commit()
        conn.close()
        
        logger.info("Database tables created/verified successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def main():
    """Main function to fix scanner look and feel issues"""
    print("\n" + "=" * 80)
    print(" Scanner and Reports Integration Fix")
    print("=" * 80)
    
    # Fix scanner CSS and customization options
    from fix_scanner_look_and_feel import check_customizations_table, check_css_files, check_template_files
    
    # Check database
    if check_customizations_table():
        print("✅ Database customizations table updated")
    else:
        print("❌ Failed to update database")
        
    # Check CSS files
    if check_css_files():
        print("✅ CSS files updated")
    else:
        print("❌ Failed to update CSS files")
        
    # Check template files
    if check_template_files():
        print("✅ Template files verified")
    else:
        print("❌ Template files may need manual updates")
    
    # Fix scanner integration
    if fix_scanner_integration():
        print("✅ Scanner routes integration fixed")
    else:
        print("❌ Failed to fix scanner routes integration")
        
    # Fix reports integration
    if fix_reports_integration():
        print("✅ Reports routes integration fixed")
    else:
        print("❌ Failed to fix reports routes integration")
    
    # Create missing tables
    if create_missing_tables():
        print("✅ Database tables created/verified")
    else:
        print("❌ Failed to create/verify database tables")
    
    print("\nScanner and reports fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()