#!/usr/bin/env python3
"""
Fix scanner appearance issues by updating the database, templates and code
"""

import os
import logging
import sqlite3
import shutil
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def fix_database_schema():
    """Ensure all required columns exist in customizations table"""
    logger.info("🔧 Fixing database schema...")
    
    # Database paths to check
    db_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db'),
        '/opt/render/project/src/client_scanner.db',
        '/home/ggrun/CybrScan_1/client_scanner.db',
        '/home/ggrun/CybrScann-main/client_scanner.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        logger.error("❌ Database not found in any of the expected locations")
        return False
        
    logger.info(f"Using database at {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check customizations table
        cursor.execute("PRAGMA table_info(customizations)")
        columns = [col[1] for col in cursor.fetchall()]
        logger.info(f"Existing columns: {columns}")
        
        # Required columns with their default values
        required_columns = {
            'button_color': "TEXT DEFAULT '#d96c33'",
            'font_family': "TEXT DEFAULT 'Roboto, sans-serif'",
            'color_style': "TEXT DEFAULT 'flat'"
        }
        
        # Add missing columns
        for column_name, column_type in required_columns.items():
            if column_name not in columns:
                try:
                    cursor.execute(f"""
                        ALTER TABLE customizations 
                        ADD COLUMN {column_name} {column_type}
                    """)
                    logger.info(f"✅ Added {column_name} column to customizations table")
                except sqlite3.OperationalError as e:
                    logger.error(f"❌ Could not add {column_name} column: {e}")
            else:
                logger.info(f"✓ {column_name} column already exists")
        
        # Update all customizations records to set button_color if NULL
        cursor.execute("""
            UPDATE customizations 
            SET button_color = '#d96c33' 
            WHERE button_color IS NULL
        """)
        
        # Update all customizations records to set font_family if NULL
        cursor.execute("""
            UPDATE customizations 
            SET font_family = 'Roboto, sans-serif' 
            WHERE font_family IS NULL
        """)
        
        # Update all customizations records to set color_style if NULL
        cursor.execute("""
            UPDATE customizations 
            SET color_style = 'flat' 
            WHERE color_style IS NULL
        """)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database schema fixed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing database schema: {e}")
        logger.error(traceback.format_exc())
        return False

def fix_css_styles():
    """Fix CSS styles to ensure proper button colors are used"""
    logger.info("🔧 Fixing CSS styles...")
    
    css_file_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/css/styles.css'),
        '/opt/render/project/src/static/css/styles.css',
        '/home/ggrun/CybrScan_1/static/css/styles.css',
        '/home/ggrun/CybrScann-main/static/css/styles.css'
    ]
    
    css_file = None
    for path in css_file_paths:
        if os.path.exists(path):
            css_file = path
            break
    
    if not css_file:
        logger.warning("⚠️ CSS file not found in any of the expected locations")
        return False
    
    logger.info(f"Using CSS file at {css_file}")
    
    try:
        # Create backup
        backup_file = f"{css_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(css_file, backup_file)
        logger.info(f"✅ Created backup at {backup_file}")
        
        # Read the CSS file
        with open(css_file, 'r') as f:
            content = f.read()
        
        # Check if button styles need to be updated
        button_styles_to_add = """
/* Scanner button styles */
.scanner-submit-btn, 
.preview-button {
    background-color: var(--button-color, #d96c33);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
}

.scanner-submit-btn:hover, 
.preview-button:hover {
    background-color: var(--primary-color, #02054c);
    transform: translateY(-2px);
    box-shadow: 0 8px 15px rgba(0,0,0,0.1);
}
"""
        
        # Add button styles if not already present
        if ".scanner-submit-btn" not in content:
            with open(css_file, 'a') as f:
                f.write("\n" + button_styles_to_add)
            logger.info("✅ Added scanner button styles to CSS")
        else:
            logger.info("✓ Scanner button styles already exist")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing CSS styles: {e}")
        logger.error(traceback.format_exc())
        return False

def fix_templates():
    """Fix scanner templates to properly handle button colors and fonts"""
    logger.info("🔧 Fixing scanner templates...")
    
    # Check if templates directory exists
    template_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
        '/opt/render/project/src/templates',
        '/home/ggrun/CybrScan_1/templates',
        '/home/ggrun/CybrScann-main/templates'
    ]
    
    templates_dir = None
    for path in template_dirs:
        if os.path.exists(path):
            templates_dir = path
            break
    
    if not templates_dir:
        logger.error("❌ Templates directory not found in any of the expected locations")
        return False
    
    logger.info(f"Using templates directory at {templates_dir}")
    
    # Files to check and fix
    template_files = [
        os.path.join(templates_dir, 'client/customize_scanner.html'),
        os.path.join(templates_dir, 'client/scanner-create.html'),
        os.path.join(templates_dir, 'client/scanner-edit.html'),
        os.path.join(templates_dir, 'client/scanner_preview.html')
    ]
    
    fixed_count = 0
    for template_file in template_files:
        if not os.path.exists(template_file):
            logger.warning(f"⚠️ Template file {template_file} not found, skipping")
            continue
            
        try:
            # Create backup
            backup_file = f"{template_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(template_file, backup_file)
            logger.info(f"✅ Created backup of {os.path.basename(template_file)} at {backup_file}")
            
            # Read the template
            with open(template_file, 'r') as f:
                content = f.read()
            
            # Check for button color input
            if 'buttonColor' not in content and 'button_color' not in content:
                logger.warning(f"⚠️ {os.path.basename(template_file)} is missing button color input")
            else:
                logger.info(f"✓ {os.path.basename(template_file)} has button color input")
            
            # Check for font family input
            if 'fontFamily' not in content and 'font_family' not in content:
                logger.warning(f"⚠️ {os.path.basename(template_file)} is missing font family input")
            else:
                logger.info(f"✓ {os.path.basename(template_file)} has font family input")
                
            fixed_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error checking template {template_file}: {e}")
            logger.error(traceback.format_exc())
    
    if fixed_count > 0:
        logger.info(f"✅ Fixed {fixed_count} template files")
        return True
    else:
        logger.warning("⚠️ No template files were fixed")
        return False

def apply_direct_fixes():
    """Apply direct fixes to code"""
    logger.info("🔧 Applying direct fixes to code...")
    
    # Copy fixed templates from CybrScann-main to CybrScan_1 if needed
    source_dir = '/home/ggrun/CybrScann-main/templates'
    target_dir = '/home/ggrun/CybrScan_1/templates'
    
    if os.path.exists(source_dir) and os.path.exists(target_dir):
        try:
            # Copy customize_scanner.html
            source_file = os.path.join(source_dir, 'client/customize_scanner.html')
            target_file = os.path.join(target_dir, 'client/customize_scanner.html')
            
            if os.path.exists(source_file):
                # Create backup of target file if it exists
                if os.path.exists(target_file):
                    backup_file = f"{target_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(target_file, backup_file)
                    logger.info(f"✅ Created backup at {backup_file}")
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                logger.info(f"✅ Copied customize_scanner.html from CybrScann-main to CybrScan_1")
            else:
                logger.warning("⚠️ Source file customize_scanner.html not found")
                
            # Copy scanner_preview.html
            source_file = os.path.join(source_dir, 'client/scanner_preview.html')
            target_file = os.path.join(target_dir, 'client/scanner_preview.html')
            
            if os.path.exists(source_file):
                # Create backup of target file if it exists
                if os.path.exists(target_file):
                    backup_file = f"{target_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(target_file, backup_file)
                    logger.info(f"✅ Created backup at {backup_file}")
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                logger.info(f"✅ Copied scanner_preview.html from CybrScann-main to CybrScan_1")
            else:
                logger.warning("⚠️ Source file scanner_preview.html not found")
                
            # Copy CSS file if exists
            source_file = os.path.join(source_dir, '../static/css/styles.css')
            target_file = os.path.join(target_dir, '../static/css/styles.css')
            
            if os.path.exists(source_file) and os.path.exists(os.path.dirname(target_file)):
                # Create backup of target file if it exists
                if os.path.exists(target_file):
                    backup_file = f"{target_file}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    shutil.copy2(target_file, backup_file)
                    logger.info(f"✅ Created backup at {backup_file}")
                
                # Copy the file
                shutil.copy2(source_file, target_file)
                logger.info(f"✅ Copied styles.css from CybrScann-main to CybrScan_1")
            else:
                logger.warning("⚠️ Source or target path for styles.css not found")
                
            return True
                
        except Exception as e:
            logger.error(f"❌ Error copying files: {e}")
            logger.error(traceback.format_exc())
            return False
    else:
        logger.warning(f"⚠️ Source or target directory not found")
        logger.warning(f"Source: {source_dir} exists: {os.path.exists(source_dir)}")
        logger.warning(f"Target: {target_dir} exists: {os.path.exists(target_dir)}")
        return False

def main():
    """Main function to fix scanner appearance"""
    print("\n" + "=" * 80)
    print(" Fixing Scanner Appearance")
    print("=" * 80)
    
    success_count = 0
    total_count = 3
    
    # Fix database schema
    if fix_database_schema():
        success_count += 1
    
    # Fix CSS styles
    if fix_css_styles():
        success_count += 1
    
    # Apply direct fixes to code
    if apply_direct_fixes():
        success_count += 1
        
    print("\n" + "=" * 80)
    print(f" Results: {success_count}/{total_count} fixes applied")
    print("=" * 80)
    
    if success_count == total_count:
        print("✅ All fixes applied successfully!")
        print("The scanner appearance should now be restored to the previous look and feel.")
        print("Restart the application to see the changes.")
    else:
        print("⚠️ Some fixes could not be applied.")
        print("Please check the logs for details.")
        
    print("=" * 80)
    
    return success_count == total_count

if __name__ == '__main__':
    main()