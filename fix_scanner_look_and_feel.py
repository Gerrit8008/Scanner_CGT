#!/usr/bin/env python3
"""
Fix scanner look and feel by ensuring proper CSS and customization options are available
"""

import os
import logging
import sqlite3
import shutil
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_customizations_table():
    """Check if customizations table has button_color and font_family columns"""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_scanner.db')
        
        if not os.path.exists(db_path):
            logger.error(f"Database not found at {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table schema
        cursor.execute("PRAGMA table_info(customizations)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        
        missing_columns = []
        if 'button_color' not in column_names:
            missing_columns.append('button_color')
        
        if 'font_family' not in column_names:
            missing_columns.append('font_family')
            
        if 'color_style' not in column_names:
            missing_columns.append('color_style')
            
        # Add missing columns
        if missing_columns:
            for column in missing_columns:
                if column == 'button_color':
                    cursor.execute("ALTER TABLE customizations ADD COLUMN button_color TEXT DEFAULT '#d96c33'")
                elif column == 'font_family':
                    cursor.execute("ALTER TABLE customizations ADD COLUMN font_family TEXT DEFAULT 'Roboto, sans-serif'")
                elif column == 'color_style':
                    cursor.execute("ALTER TABLE customizations ADD COLUMN color_style TEXT DEFAULT 'flat'")
            
            conn.commit()
            logger.info(f"Added missing columns to customizations table: {', '.join(missing_columns)}")
        else:
            logger.info("All required columns exist in customizations table")
        
        # Set default values for existing rows
        cursor.execute("""
            UPDATE customizations 
            SET button_color = '#d96c33' 
            WHERE button_color IS NULL
        """)
        
        cursor.execute("""
            UPDATE customizations 
            SET font_family = 'Roboto, sans-serif' 
            WHERE font_family IS NULL
        """)
        
        cursor.execute("""
            UPDATE customizations 
            SET color_style = 'flat' 
            WHERE color_style IS NULL
        """)
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error checking customizations table: {e}")
        return False

def check_css_files():
    """Check if CSS files have the necessary styles"""
    try:
        # Check if scanner_buttons.css exists
        scanner_buttons_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/css/scanner_buttons.css')
        
        if not os.path.exists(scanner_buttons_path):
            logger.error(f"Scanner buttons CSS not found at {scanner_buttons_path}")
            return False
        
        # Check if styles.css has button-color variable
        styles_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/css/styles.css')
        
        if not os.path.exists(styles_path):
            logger.error(f"Styles CSS not found at {styles_path}")
            return False
        
        with open(styles_path, 'r') as f:
            styles_content = f.read()
            
        if '--button-color:' not in styles_content:
            # Add button-color variable to root
            styles_content = styles_content.replace(
                ':root {', 
                ':root {\n    --button-color: #d96c33;'
            )
            
            with open(styles_path, 'w') as f:
                f.write(styles_content)
                
            logger.info("Added button-color variable to styles.css")
        
        # Ensure scanner button styles are included
        if '.scanner-submit-btn' not in styles_content:
            # Append scanner button styles
            with open(scanner_buttons_path, 'r') as f:
                button_styles = f.read()
                
            with open(styles_path, 'a') as f:
                f.write('\n\n' + button_styles)
                
            logger.info("Added scanner button styles to styles.css")
        
        return True
    except Exception as e:
        logger.error(f"Error checking CSS files: {e}")
        return False

def check_template_files():
    """Check if template files have been updated"""
    try:
        # Check customize_scanner.html
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    'templates/client/customize_scanner.html')
        
        if not os.path.exists(template_path):
            logger.error(f"Template not found at {template_path}")
            return False
        
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Check if button color input exists
        if 'id="buttonColor"' not in template_content:
            logger.warning("Button color input not found in customize_scanner.html")
            return False
            
        # Check if button color event listeners exist
        if "document.getElementById('buttonColor').addEventListener" not in template_content:
            logger.warning("Button color event listeners not found in customize_scanner.html")
            return False
            
        logger.info("Template files have been properly updated")
        return True
    except Exception as e:
        logger.error(f"Error checking template files: {e}")
        return False

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" Scanner Look and Feel Fix")
    print("=" * 80)
    
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
    
    print("\nScanner look and feel fixes have been applied!")
    print("=" * 80)

if __name__ == "__main__":
    main()