#!/usr/bin/env python3
"""
Update Subscription Levels

This script updates the subscription levels in CybrScann-main to match those in CybrScan_1,
making "basic" the default level and ensuring all limits and details are preserved.
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Subscription level definitions
SUBSCRIPTION_LEVELS = {
    'basic': {
        'name': 'Basic',
        'price': 0.00,  # Free
        'period': 'forever',
        'description': 'Perfect for trying out our platform',
        'features': {
            'scanners': 1,
            'scans_per_month': 10,
            'white_label': False,
            'branding': 'Basic branding',
            'reports': 'Email reports',
            'support': 'Community support',
            'api_access': False,
            'client_portal': False
        }
    },
    'starter': {
        'name': 'Starter',
        'price': 59.99,
        'period': 'month',
        'description': 'Perfect for small MSPs getting started',
        'features': {
            'scanners': 1,
            'scans_per_month': 50,
            'white_label': True,
            'branding': 'White-label branding',
            'reports': 'Basic reporting',
            'support': 'Email support',
            'api_access': False,
            'client_portal': True,
            'integrations': 'Basic integrations'
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 99.99,
        'period': 'month',
        'description': 'Ideal for growing MSPs',
        'popular': True,
        'features': {
            'scanners': 3,
            'scans_per_month': 500,
            'white_label': True,
            'branding': 'Advanced white-labeling',
            'reports': 'Professional reporting',
            'support': 'Priority phone support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom integrations',
            'scheduled_scanning': True
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 149.99,
        'period': 'month',
        'description': 'For large MSPs and enterprises',
        'features': {
            'scanners': 10,
            'scans_per_month': 1000,
            'white_label': True,
            'branding': 'Complete white-labeling',
            'reports': 'Executive reporting',
            'support': '24/7 dedicated support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom development',
            'scheduled_scanning': True,
            'sla': True,
            'training': True,
            'multi_tenant': True
        }
    }
}

def get_db_connection():
    """Get a connection to the database"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def update_database_schema():
    """Update the database schema to support the new subscription levels"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the subscription_details column exists
        cursor.execute("PRAGMA table_info(clients)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add new columns if they don't exist
        if 'subscription_details' not in columns:
            logger.info("Adding subscription_details column to clients table")
            cursor.execute("ALTER TABLE clients ADD COLUMN subscription_details TEXT")
        
        if 'scan_limit' not in columns:
            logger.info("Adding scan_limit column to clients table")
            cursor.execute("ALTER TABLE clients ADD COLUMN scan_limit INTEGER DEFAULT 10")
        
        if 'scanner_limit' not in columns:
            logger.info("Adding scanner_limit column to clients table")
            cursor.execute("ALTER TABLE clients ADD COLUMN scanner_limit INTEGER DEFAULT 1")
        
        conn.commit()
        conn.close()
        logger.info("Database schema updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating database schema: {e}")
        return False

def update_subscription_levels():
    """Update existing subscription levels in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all clients
        cursor.execute("SELECT id, subscription_level FROM clients")
        clients = cursor.fetchall()
        
        # Update client subscriptions
        for client in clients:
            client_id = client['id']
            current_level = client['subscription_level']
            
            # Map old subscription levels to new ones
            # If the level doesn't match any of our new levels, set it to 'basic'
            if current_level not in SUBSCRIPTION_LEVELS:
                if current_level == 'pro':
                    new_level = 'professional'
                elif current_level == 'premium':
                    new_level = 'professional'
                elif current_level == 'custom':
                    new_level = 'enterprise'
                else:
                    new_level = 'basic'
            else:
                new_level = current_level
            
            # Set subscription details
            subscription_details = json.dumps(SUBSCRIPTION_LEVELS[new_level])
            
            # Set limits based on subscription level
            scan_limit = SUBSCRIPTION_LEVELS[new_level]['features']['scans_per_month']
            scanner_limit = SUBSCRIPTION_LEVELS[new_level]['features']['scanners']
            
            # Update the client record
            cursor.execute("""
                UPDATE clients
                SET subscription_level = ?,
                    subscription_details = ?,
                    scan_limit = ?,
                    scanner_limit = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                new_level,
                subscription_details,
                scan_limit,
                scanner_limit,
                datetime.now().isoformat(),
                client_id
            ))
            
            logger.info(f"Updated client {client_id} from {current_level} to {new_level}")
        
        conn.commit()
        conn.close()
        logger.info("Subscription levels updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating subscription levels: {e}")
        return False

def update_pricing_template():
    """Update the pricing template to reflect the new subscription levels"""
    try:
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/partials/pricing-cards.html')
        
        # Make a backup of the original file
        backup_path = template_path + '.bak'
        with open(template_path, 'r') as f:
            original_content = f.read()
            
        with open(backup_path, 'w') as f:
            f.write(original_content)
            
        # Create new pricing cards content
        new_content = """<!-- MSP Pricing Plans - Updated with 4 tiers -->
<div class="row g-4">
    <!-- Basic Plan -->
    <div class="col-lg-3 col-md-6">
        <div class="card h-100">
            <div class="card-header text-center">
                <h5 class="plan-name">Basic</h5>
                <div class="price">Free<span class="price-period">/forever</span></div>
                <p class="plan-description">Perfect for trying out our platform</p>
            </div>
            <div class="card-body">
                <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i>1 scanner</li>
                    <li><i class="bi bi-check-circle-fill"></i>10 scans per month</li>
                    <li><i class="bi bi-check-circle-fill"></i>Basic branding</li>
                    <li><i class="bi bi-check-circle-fill"></i>Email reports</li>
                    <li><i class="bi bi-check-circle-fill"></i>Community support</li>
                    <li><i class="bi bi-x-circle-fill text-muted"></i><span class="text-muted">No API access</span></li>
                </ul>
                <div class="text-center mt-auto">
                    <a href="/auth/register?plan=basic" class="btn btn-outline-primary btn-pricing">Get Started Free</a>
                </div>
            </div>
        </div>
    </div>

    <!-- Starter Plan -->
    <div class="col-lg-3 col-md-6">
        <div class="card h-100">
            <div class="card-header text-center">
                <h5 class="plan-name">Starter</h5>
                <div class="price">$59<span class="price-period">/month</span></div>
                <p class="plan-description">Perfect for small MSPs getting started</p>
            </div>
            <div class="card-body">
                <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i>1 scanner</li>
                    <li><i class="bi bi-check-circle-fill"></i>50 scans per month</li>
                    <li><i class="bi bi-check-circle-fill"></i>White-label branding</li>
                    <li><i class="bi bi-check-circle-fill"></i>Basic reporting</li>
                    <li><i class="bi bi-check-circle-fill"></i>Email support</li>
                    <li><i class="bi bi-check-circle-fill"></i>Client portal access</li>
                    <li><i class="bi bi-check-circle-fill"></i>Basic integrations</li>
                </ul>
                <div class="text-center mt-auto">
                    <a href="/auth/register?plan=starter" class="btn btn-outline-primary btn-pricing">Get Started</a>
                </div>
            </div>
        </div>
    </div>

    <!-- Professional Plan -->
    <div class="col-lg-3 col-md-6">
        <div class="card h-100 border-primary featured">
            <div class="popular-badge">Most Popular</div>
            <div class="card-header text-center bg-primary text-white">
                <h5 class="plan-name">Professional</h5>
                <div class="price">$99<span class="price-period">/month</span></div>
                <p class="plan-description">Ideal for growing MSPs</p>
            </div>
            <div class="card-body">
                <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i>3 scanners</li>
                    <li><i class="bi bi-check-circle-fill"></i>500 scans per month</li>
                    <li><i class="bi bi-check-circle-fill"></i>Advanced white-labeling</li>
                    <li><i class="bi bi-check-circle-fill"></i>Professional reporting</li>
                    <li><i class="bi bi-check-circle-fill"></i>Priority phone support</li>
                    <li><i class="bi bi-check-circle-fill"></i>Advanced client portal</li>
                    <li><i class="bi bi-check-circle-fill"></i>API access</li>
                    <li><i class="bi bi-check-circle-fill"></i>Custom integrations</li>
                    <li><i class="bi bi-check-circle-fill"></i>Scheduled scanning</li>
                </ul>
                <div class="text-center mt-auto">
                    <a href="/auth/register?plan=professional" class="btn btn-light btn-pricing">Start Free Trial</a>
                </div>
            </div>
        </div>
    </div>

    <!-- Enterprise Plan -->
    <div class="col-lg-3 col-md-6">
        <div class="card h-100">
            <div class="card-header text-center">
                <h5 class="plan-name">Enterprise</h5>
                <div class="price">$149<span class="price-period">/month</span></div>
                <p class="plan-description">For large MSPs and enterprises</p>
            </div>
            <div class="card-body">
                <ul class="features-list">
                    <li><i class="bi bi-check-circle-fill"></i>10 scanners</li>
                    <li><i class="bi bi-check-circle-fill"></i>1000 scans per month</li>
                    <li><i class="bi bi-check-circle-fill"></i>Complete white-labeling</li>
                    <li><i class="bi bi-check-circle-fill"></i>Executive reporting</li>
                    <li><i class="bi bi-check-circle-fill"></i>24/7 dedicated support</li>
                    <li><i class="bi bi-check-circle-fill"></i>Multi-tenant management</li>
                    <li><i class="bi bi-check-circle-fill"></i>Full API access</li>
                    <li><i class="bi bi-check-circle-fill"></i>Custom development</li>
                    <li><i class="bi bi-check-circle-fill"></i>SLA guarantees</li>
                    <li><i class="bi bi-check-circle-fill"></i>Training & onboarding</li>
                </ul>
                <div class="text-center mt-auto">
                    <a href="/contact?plan=enterprise" class="btn btn-outline-primary btn-pricing">Contact Sales</a>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Pricing Card Styles -->
<style>
.pricing-cards .card {
    border: 1px solid #dee2e6;
    border-radius: 15px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.pricing-cards .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(26, 35, 126, 0.15);
}

.pricing-cards .card.featured {
    transform: scale(1.05);
    border-color: var(--primary-color);
}

.pricing-cards .card.featured:hover {
    transform: scale(1.05) translateY(-5px);
}

.pricing-cards .plan-name {
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.pricing-cards .plan-description {
    font-size: 0.9rem;
    opacity: 0.8;
    margin-bottom: 0;
}

.pricing-cards .price {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--accent-green);
    margin: 0.5rem 0;
}

.pricing-cards .card.featured .price {
    color: var(--accent-green);
}

.pricing-cards .price-period {
    font-size: 1rem;
    opacity: 0.7;
}

.pricing-cards .features-list {
    list-style: none;
    padding: 0;
    margin: 1rem 0;
}

.pricing-cards .features-list li {
    padding: 0.5rem 0;
    display: flex;
    align-items: center;
}

.pricing-cards .features-list li i {
    color: var(--accent-green);
    margin-right: 0.75rem;
    font-size: 1.1rem;
}

.pricing-cards .btn-pricing {
    width: 100%;
    padding: 0.75rem;
    font-weight: 600;
    border-radius: 50px;
    transition: all 0.3s ease;
}

.pricing-cards .popular-badge {
    position: absolute;
    top: 20px;
    right: -35px;
    background: var(--accent-green);
    color: var(--primary-color);
    padding: 5px 40px;
    font-size: 0.8rem;
    font-weight: 600;
    transform: rotate(45deg);
    text-transform: uppercase;
    z-index: 10;
}
</style>"""
        
        # Write the new content to the file
        with open(template_path, 'w') as f:
            f.write(new_content)
            
        logger.info("Pricing template updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating pricing template: {e}")
        # Restore from backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            with open(template_path, 'w') as f:
                f.write(backup_content)
            logger.info("Restored original pricing template from backup")
        return False

def update_subscription_routes():
    """Update the subscription_routes.py file to use the new subscription levels"""
    try:
        routes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subscription_routes.py')
        
        # Check if the file exists
        if not os.path.exists(routes_path):
            logger.warning("subscription_routes.py not found, skipping update")
            return True
        
        # Make a backup of the original file
        backup_path = routes_path + '.bak'
        with open(routes_path, 'r') as f:
            original_content = f.read()
            
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        # Replace subscription level calculations
        updated_content = original_content.replace(
            """CASE 
                    WHEN subscription_level = 'basic' THEN 49
                    WHEN subscription_level = 'pro' THEN 149
                    WHEN subscription_level = 'enterprise' THEN 399
                    ELSE 0
                END""",
            """CASE 
                    WHEN subscription_level = 'basic' THEN 0
                    WHEN subscription_level = 'starter' THEN 59
                    WHEN subscription_level = 'professional' THEN 99
                    WHEN subscription_level = 'enterprise' THEN 149
                    ELSE 0
                END"""
        )
        
        # Update filter calculations for stats
        updated_content = updated_content.replace(
            """SUM(CASE WHEN subscription_level = 'basic' THEN 1 ELSE 0 END) as basic_count,
                SUM(CASE WHEN subscription_level = 'pro' THEN 1 ELSE 0 END) as pro_count,
                SUM(CASE WHEN subscription_level = 'enterprise' THEN 1 ELSE 0 END) as enterprise_count""",
            """SUM(CASE WHEN subscription_level = 'basic' THEN 1 ELSE 0 END) as basic_count,
                SUM(CASE WHEN subscription_level = 'starter' THEN 1 ELSE 0 END) as starter_count,
                SUM(CASE WHEN subscription_level = 'professional' THEN 1 ELSE 0 END) as professional_count,
                SUM(CASE WHEN subscription_level = 'enterprise' THEN 1 ELSE 0 END) as enterprise_count"""
        )
        
        # Write the updated content to the file
        with open(routes_path, 'w') as f:
            f.write(updated_content)
            
        logger.info("Subscription routes updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating subscription routes: {e}")
        # Restore from backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            with open(routes_path, 'w') as f:
                f.write(backup_content)
            logger.info("Restored original subscription routes from backup")
        return False

def update_client_registration():
    """Update client registration to use the new subscription levels"""
    try:
        # Find registration route file - likely in auth.py or similar
        auth_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auth.py')
        
        if not os.path.exists(auth_file_path):
            logger.warning("auth.py not found, skipping update")
            return True
        
        # Make a backup of the original file
        backup_path = auth_file_path + '.bak'
        with open(auth_file_path, 'r') as f:
            original_content = f.read()
            
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        # Read the file content and look for registration function
        with open(auth_file_path, 'r') as f:
            content = f.read()
        
        # Check if 'subscription_level' is being set during registration
        if 'subscription_level' in content and '/register' in content:
            # Update to set proper defaults
            updated_content = content.replace(
                "subscription_level = 'basic'",
                "subscription_level = request.args.get('plan', 'basic')"
            )
            
            # Handle subscription limits based on level
            if 'scan_limit' not in content and 'scanner_limit' not in content:
                # Find the registration function - look for where client is created
                client_creation_pattern = "INSERT INTO clients"
                if client_creation_pattern in updated_content:
                    # Extract the client creation section
                    parts = updated_content.split(client_creation_pattern)
                    
                    # Add code to set limits based on subscription level before client creation
                    limits_code = """
            # Set limits based on subscription level
            if subscription_level == 'basic':
                scan_limit = 10
                scanner_limit = 1
            elif subscription_level == 'starter':
                scan_limit = 50
                scanner_limit = 1
            elif subscription_level == 'professional':
                scan_limit = 500
                scanner_limit = 3
            elif subscription_level == 'enterprise':
                scan_limit = 1000
                scanner_limit = 10
            else:
                scan_limit = 10
                scanner_limit = 1
                
            # Create subscription details JSON
            subscription_details = json.dumps({
                'name': subscription_level.capitalize(),
                'features': {
                    'scanners': scanner_limit,
                    'scans_per_month': scan_limit
                }
            })
            
            """
                    
                    # Add the limits code before client creation
                    updated_content = parts[0] + limits_code + client_creation_pattern + parts[1]
                    
                    # Make sure json is imported
                    if "import json" not in updated_content:
                        import_section_end = updated_content.find("\n\n", updated_content.find("import"))
                        updated_content = updated_content[:import_section_end] + "\nimport json" + updated_content[import_section_end:]
            
            # Update the file with the new content
            with open(auth_file_path, 'w') as f:
                f.write(updated_content)
            
            logger.info("Client registration updated successfully")
            return True
        else:
            logger.warning("Could not locate subscription_level in registration, manual update needed")
            return True
    except Exception as e:
        logger.error(f"Error updating client registration: {e}")
        # Restore from backup if it exists
        if os.path.exists(backup_path):
            with open(backup_path, 'r') as f:
                backup_content = f.read()
            with open(auth_file_path, 'w') as f:
                f.write(backup_content)
            logger.info("Restored original auth file from backup")
        return False

def create_subscription_constants_file():
    """Create a constants file for subscription levels"""
    try:
        constants_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subscription_constants.py')
        
        content = """#!/usr/bin/env python3
\"\"\"
Subscription Constants

This file defines the subscription levels and their features.
\"\"\"

# Subscription level definitions
SUBSCRIPTION_LEVELS = {
    'basic': {
        'name': 'Basic',
        'price': 0.00,  # Free
        'period': 'forever',
        'description': 'Perfect for trying out our platform',
        'features': {
            'scanners': 1,
            'scans_per_month': 10,
            'white_label': False,
            'branding': 'Basic branding',
            'reports': 'Email reports',
            'support': 'Community support',
            'api_access': False,
            'client_portal': False
        }
    },
    'starter': {
        'name': 'Starter',
        'price': 59.99,
        'period': 'month',
        'description': 'Perfect for small MSPs getting started',
        'features': {
            'scanners': 1,
            'scans_per_month': 50,
            'white_label': True,
            'branding': 'White-label branding',
            'reports': 'Basic reporting',
            'support': 'Email support',
            'api_access': False,
            'client_portal': True,
            'integrations': 'Basic integrations'
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 99.99,
        'period': 'month',
        'description': 'Ideal for growing MSPs',
        'popular': True,
        'features': {
            'scanners': 3,
            'scans_per_month': 500,
            'white_label': True,
            'branding': 'Advanced white-labeling',
            'reports': 'Professional reporting',
            'support': 'Priority phone support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom integrations',
            'scheduled_scanning': True
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 149.99,
        'period': 'month',
        'description': 'For large MSPs and enterprises',
        'features': {
            'scanners': 10,
            'scans_per_month': 1000,
            'white_label': True,
            'branding': 'Complete white-labeling',
            'reports': 'Executive reporting',
            'support': '24/7 dedicated support',
            'api_access': True,
            'client_portal': True,
            'integrations': 'Custom development',
            'scheduled_scanning': True,
            'sla': True,
            'training': True,
            'multi_tenant': True
        }
    }
}

def get_subscription_features(level):
    \"\"\"Get the features for a subscription level\"\"\"
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    return SUBSCRIPTION_LEVELS[level]

def get_subscription_limit(level, limit_type):
    \"\"\"Get a specific limit for a subscription level\"\"\"
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    
    features = SUBSCRIPTION_LEVELS[level]['features']
    if limit_type == 'scanners':
        return features.get('scanners', 1)
    elif limit_type == 'scans':
        return features.get('scans_per_month', 10)
    else:
        return None

def get_subscription_price(level):
    \"\"\"Get the price for a subscription level\"\"\"
    if level not in SUBSCRIPTION_LEVELS:
        level = 'basic'  # Default to basic if level not found
    return SUBSCRIPTION_LEVELS[level]['price']
"""
        
        with open(constants_path, 'w') as f:
            f.write(content)
            
        logger.info("Subscription constants file created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating subscription constants file: {e}")
        return False

def main():
    """Main function to run the update process"""
    logger.info("Starting subscription levels update")
    
    # Update database schema
    if not update_database_schema():
        logger.error("Failed to update database schema, aborting")
        return
    
    # Update subscription levels in the database
    if not update_subscription_levels():
        logger.error("Failed to update subscription levels, aborting")
        return
    
    # Update pricing template
    if not update_pricing_template():
        logger.warning("Failed to update pricing template, continuing anyway")
    
    # Update subscription routes
    if not update_subscription_routes():
        logger.warning("Failed to update subscription routes, continuing anyway")
    
    # Update client registration
    if not update_client_registration():
        logger.warning("Failed to update client registration, continuing anyway")
    
    # Create subscription constants file
    if not create_subscription_constants_file():
        logger.warning("Failed to create subscription constants file, continuing anyway")
    
    logger.info("Subscription levels update completed successfully")

if __name__ == "__main__":
    main()