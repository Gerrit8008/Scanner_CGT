#!/usr/bin/env python3
"""
Subscription Limit Patch

This patch can be applied to enforce subscription limits in scan.py
or any other file that handles scan creation. The patch will check if a client
has reached their scan limit before allowing a new scan to be created.
"""

# Import this function at the top of your scan.py file
def check_scan_limit(client_id, conn=None, cursor=None):
    """
    Check if a client has reached their scan limit
    
    Args:
        client_id (int): The client ID to check
        conn (sqlite3.Connection, optional): Database connection
        cursor (sqlite3.Cursor, optional): Database cursor
        
    Returns:
        tuple: (has_reached_limit, limit, current_count, remaining)
    """
    import os
    import sqlite3
    from datetime import datetime
    
    # Create connection if not provided
    close_conn = False
    if conn is None or cursor is None:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True
    
    try:
        # Get client subscription level and scan limit
        cursor.execute("""
            SELECT id, subscription_level, scan_limit
            FROM clients 
            WHERE id = ?
        """, (client_id,))
        
        client = cursor.fetchone()
        if not client:
            return (False, 0, 0, 0)
        
        # Get subscription level
        subscription_level = client['subscription_level'] if hasattr(client, 'keys') else client[1]
        
        # Get scan limit from client record or subscription constants
        scan_limit_value = client['scan_limit'] if hasattr(client, 'keys') else client[2]
        
        if scan_limit_value is not None:
            scan_limit = scan_limit_value
        else:
            # Default limits based on subscription level
            if subscription_level == 'basic':
                scan_limit = 10
            elif subscription_level == 'starter':
                scan_limit = 50
            elif subscription_level == 'professional':
                scan_limit = 500
            elif subscription_level == 'enterprise':
                scan_limit = 1000
            else:
                scan_limit = 10  # Default for unknown levels
        
        # Calculate the start of the current month
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # Count scans for this month from scan_history
        try:
            cursor.execute("""
                SELECT COUNT(*) as scan_count
                FROM scan_history sh
                JOIN scanners s ON sh.scanner_id = s.scanner_id
                WHERE s.client_id = ? AND sh.created_at >= ?
            """, (client_id, current_month_start))
            
            scan_count_row = cursor.fetchone()
            scan_count = scan_count_row[0] if scan_count_row else 0
        except:
            # Table might not exist
            scan_count = 0
        
        # Also check scans table if scan_history fails
        if scan_count == 0:
            try:
                cursor.execute("""
                    SELECT COUNT(*) as scan_count
                    FROM scans
                    WHERE client_id = ? AND timestamp >= ?
                """, (client_id, current_month_start))
                
                scan_count_row = cursor.fetchone()
                scan_count = scan_count_row[0] if scan_count_row else 0
            except:
                # Table might not exist
                scan_count = 0
        
        # Also check client-specific database if it exists
        client_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                      f'client_databases/client_{client_id}_scans.db')
        
        if os.path.exists(client_db_path):
            try:
                client_conn = sqlite3.connect(client_db_path)
                client_cursor = client_conn.cursor()
                
                # Check if scans table exists
                client_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
                if client_cursor.fetchone():
                    # Count scans for this month
                    client_cursor.execute("""
                        SELECT COUNT(*) as scan_count
                        FROM scans
                        WHERE timestamp >= ?
                    """, (current_month_start,))
                    
                    client_scan_count_row = client_cursor.fetchone()
                    client_scan_count = client_scan_count_row[0] if client_scan_count_row else 0
                    
                    # Add to total scan count
                    scan_count += client_scan_count
                
                client_conn.close()
            except:
                # Could not access client database
                pass
        
        # Check if limit is reached
        has_reached_limit = scan_count >= scan_limit
        remaining = max(0, scan_limit - scan_count)
        
        if close_conn:
            conn.close()
            
        return (has_reached_limit, scan_limit, scan_count, remaining)
    except Exception as e:
        # Log error but don't block scans if checking fails
        print(f"Error checking scan limit: {e}")
        if close_conn:
            conn.close()
        return (False, 0, 0, 0)

# Import this function at the top of your scanner.py file
def check_scanner_limit(client_id, conn=None, cursor=None):
    """
    Check if a client has reached their scanner limit
    
    Args:
        client_id (int): The client ID to check
        conn (sqlite3.Connection, optional): Database connection
        cursor (sqlite3.Cursor, optional): Database cursor
        
    Returns:
        tuple: (has_reached_limit, limit, current_count, remaining)
    """
    # Create connection if not provided
    close_conn = False
    if conn is None or cursor is None:
        from client_db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True
    
    try:
        # Get client subscription level and scanner limit
        cursor.execute("""
            SELECT id, subscription_level, scanner_limit
            FROM clients 
            WHERE id = ?
        """, (client_id,))
        
        client = cursor.fetchone()
        if not client:
            return (False, 0, 0, 0)
        
        # Get subscription level
        subscription_level = client['subscription_level'] if hasattr(client, 'keys') else client[1]
        
        # Get scanner limit from client record or default values
        scanner_limit_value = client['scanner_limit'] if hasattr(client, 'keys') else client[2]
        
        if scanner_limit_value is not None:
            scanner_limit = scanner_limit_value
        else:
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
        cursor.execute("""
            SELECT COUNT(*) as scanner_count
            FROM scanners
            WHERE client_id = ? AND status != 'deleted'
        """, (client_id,))
        
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

# Example usage in scan.py
"""
# Add this check before creating a new scan
from subscription_limit_patch import check_scan_limit

@app.route('/api/scan', methods=['POST'])
def create_scan():
    # Get client ID from the request
    client_id = get_client_id_from_request()
    
    # Check if client has reached their scan limit
    has_reached_limit, limit, count, remaining = check_scan_limit(client_id)
    
    if has_reached_limit:
        return jsonify({
            'status': 'error',
            'message': f'Scan limit reached. Your subscription allows {limit} scans per month. You have used {count} scans this month.',
            'remaining': remaining
        }), 403
    
    # Continue with scan creation
    # ...
"""

# Example usage in scanner.py
"""
# Add this check before creating a new scanner
from subscription_limit_patch import check_scanner_limit

@app.route('/api/scanners', methods=['POST'])
def create_scanner():
    # Get client ID from the request
    client_id = get_client_id_from_request()
    
    # Check if client has reached their scanner limit
    has_reached_limit, limit, count, remaining = check_scanner_limit(client_id)
    
    if has_reached_limit:
        return jsonify({
            'status': 'error',
            'message': f'Scanner limit reached. Your subscription allows {limit} scanners. You have created {count} scanners.',
            'remaining': remaining
        }), 403
    
    # Continue with scanner creation
    # ...
"""

# Documentation about integrating the subscription limit patch
"""
Integration Guide for Subscription Limit Patch

1. Import the check functions at the top of your file:
   from subscription_limit_patch import check_scan_limit, check_scanner_limit

2. Add the check before creating a new scan or scanner:
   has_reached_limit, limit, count, remaining = check_scan_limit(client_id)
   if has_reached_limit:
       # Return an error response or redirect to an upgrade page

3. The functions return a tuple with four values:
   - has_reached_limit: True if the client has reached their limit
   - limit: The client's current limit
   - count: The number of scans or scanners used
   - remaining: The number of scans or scanners remaining

4. You can also check the remaining scans in a template:
   {% if remaining_scans <= 5 %}
       <div class="alert alert-warning">
           You have {{ remaining_scans }} scans remaining this month.
           <a href="{{ url_for('subscription.upgrade') }}">Upgrade your plan</a> for more scans.
       </div>
   {% endif %}
"""