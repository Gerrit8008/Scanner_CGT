#!/usr/bin/env python3
"""
Update Subscription Routes

This script updates the subscription_routes.py file to use the new pricing structure:
- Basic: Free
- Starter: $59/month
- Professional: $99/month
- Enterprise: $149/month
"""

import os
import re
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_subscription_routes():
    """Update the subscription_routes.py file to use the new pricing"""
    try:
        # Get the path to the subscription_routes.py file
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subscription_routes.py')
        
        # Check if the file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        
        # Create a backup of the original file
        backup_path = f"{file_path}.bak"
        with open(file_path, 'r') as f:
            original_content = f.read()
        
        with open(backup_path, 'w') as f:
            f.write(original_content)
            
        logger.info(f"Created backup at {backup_path}")
        
        # Update the pricing structure
        updated_content = original_content
        
        # Replace the first monthly revenue calculation
        first_revenue_pattern = r"""SELECT SUM\(\s*
                CASE\s*
                    WHEN subscription_level = 'basic' THEN 49\s*
                    WHEN subscription_level = 'pro' THEN 149\s*
                    WHEN subscription_level = 'enterprise' THEN 399\s*
                    ELSE 0\s*
                END\s*
            \) as monthly_revenue"""
        
        first_revenue_replacement = """SELECT SUM(
                CASE 
                    WHEN subscription_level = 'basic' THEN 0
                    WHEN subscription_level = 'starter' THEN 59
                    WHEN subscription_level = 'professional' THEN 99
                    WHEN subscription_level = 'enterprise' THEN 149
                    ELSE 0
                END
            ) as monthly_revenue"""
        
        updated_content = re.sub(first_revenue_pattern, first_revenue_replacement, updated_content, flags=re.MULTILINE)
        
        # Replace the second monthly revenue calculation
        second_revenue_pattern = r"""SELECT SUM\(\s*
                CASE\s*
                    WHEN subscription_level = 'basic' THEN 49\s*
                    WHEN subscription_level = 'pro' THEN 149\s*
                    WHEN subscription_level = 'enterprise' THEN 399\s*
                    ELSE 0\s*
                END\s*
            \) as monthly_revenue"""
        
        second_revenue_replacement = """SELECT SUM(
                CASE 
                    WHEN subscription_level = 'basic' THEN 0
                    WHEN subscription_level = 'starter' THEN 59
                    WHEN subscription_level = 'professional' THEN 99
                    WHEN subscription_level = 'enterprise' THEN 149
                    ELSE 0
                END
            ) as monthly_revenue"""
        
        updated_content = re.sub(second_revenue_pattern, second_revenue_replacement, updated_content, flags=re.MULTILINE)
        
        # Replace the subscription level counts
        count_pattern = r"""COUNT\(\*\) as total_count,\s*
                SUM\(CASE WHEN subscription_status = 'active' THEN 1 ELSE 0 END\) as active_count,\s*
                SUM\(CASE WHEN subscription_level = 'basic' THEN 1 ELSE 0 END\) as basic_count,\s*
                SUM\(CASE WHEN subscription_level = 'pro' THEN 1 ELSE 0 END\) as pro_count,\s*
                SUM\(CASE WHEN subscription_level = 'enterprise' THEN 1 ELSE 0 END\) as enterprise_count"""
        
        count_replacement = """COUNT(*) as total_count,
                SUM(CASE WHEN subscription_status = 'active' THEN 1 ELSE 0 END) as active_count,
                SUM(CASE WHEN subscription_level = 'basic' THEN 1 ELSE 0 END) as basic_count,
                SUM(CASE WHEN subscription_level = 'starter' THEN 1 ELSE 0 END) as starter_count,
                SUM(CASE WHEN subscription_level = 'professional' THEN 1 ELSE 0 END) as professional_count,
                SUM(CASE WHEN subscription_level = 'enterprise' THEN 1 ELSE 0 END) as enterprise_count"""
        
        updated_content = re.sub(count_pattern, count_replacement, updated_content, flags=re.MULTILINE)
        
        # Write the updated content back to the file
        with open(file_path, 'w') as f:
            f.write(updated_content)
            
        logger.info("Updated subscription_routes.py successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error updating subscription_routes.py: {e}")
        
        # Restore the backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                original_content = f.read()
            
            with open(file_path, 'w') as f:
                f.write(original_content)
                
            logger.info("Restored backup after error")
            
        return False

if __name__ == "__main__":
    if update_subscription_routes():
        print("✅ Successfully updated subscription_routes.py")
    else:
        print("❌ Failed to update subscription_routes.py")