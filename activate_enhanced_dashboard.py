#!/usr/bin/env python3
"""
Activation module for enhanced admin dashboard

This module is designed to be imported in the app.py file
to automatically activate the enhanced admin dashboard on startup.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def activate_enhanced_dashboard():
    """
    Activate the enhanced admin dashboard
    
    This function is called when the application starts.
    It loads the enhanced_admin_dashboard module and applies the enhancements.
    """
    try:
        logger.info("🔄 Activating enhanced admin dashboard...")
        from enhanced_admin_dashboard import enhance_admin_dashboard
        success = enhance_admin_dashboard()
        
        if success:
            logger.info("✅ Enhanced admin dashboard activated successfully")
        else:
            logger.warning("⚠️ Failed to activate enhanced admin dashboard")
            
        return success
    except Exception as e:
        logger.error(f"❌ Error activating enhanced admin dashboard: {str(e)}")
        return False

# Auto-execute when imported
activate_enhanced_dashboard()