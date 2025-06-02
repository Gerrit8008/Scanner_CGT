#!/usr/bin/env python3
"""
Script to apply the enhanced admin dashboard
"""

import logging
from enhanced_admin_dashboard import enhance_admin_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to apply the enhanced admin dashboard"""
    print("=" * 50)
    print("Applying Enhanced Admin Dashboard")
    print("=" * 50)
    
    try:
        # Apply the enhanced admin dashboard
        success = enhance_admin_dashboard()
        
        if success:
            print("\n✅ Enhanced admin dashboard applied successfully!")
            print("\nThe admin dashboard now displays comprehensive data including:")
            print("  - Detailed client information")
            print("  - Scanner deployment statistics")
            print("  - Lead generation data")
            print("  - System health metrics")
            print("  - User activity tracking")
            print("\nAccess the enhanced dashboard at: /admin/dashboard")
        else:
            print("\n❌ Failed to apply enhanced admin dashboard")
            print("Please check the logs for details")
    except Exception as e:
        logger.error(f"Error applying enhanced admin dashboard: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        print("Please check the logs for details")

if __name__ == "__main__":
    main()