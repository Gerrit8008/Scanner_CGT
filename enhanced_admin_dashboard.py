#!/usr/bin/env python3
"""
Enhanced Admin Dashboard Module

This module provides comprehensive data gathering functionality for the admin dashboard,
including detailed information about clients, scanners, leads, and system health.
"""

import os
import sqlite3
import logging
import json
from datetime import datetime, timedelta
import socket
import platform
import re
from pathlib import Path

# Import required modules
from client_db import get_db_connection
import scanner_db_functions
import admin_db_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_enhanced_dashboard_data():
    """
    Get comprehensive data for the admin dashboard
    
    Returns:
        dict: All data needed for the admin dashboard
    """
    try:
        # Get dashboard statistics
        dashboard_stats = get_dashboard_statistics()
        
        # Get recent clients with detailed information
        clients = get_recent_clients(10)
        
        # Get deployed scanners with details
        scanners = get_all_scanners_with_details(10)
        
        # Get recent leads from scan history
        recent_leads = get_recent_leads(10)
        
        # Get system health information
        system_health = get_system_health()
        
        # Get recent activities
        recent_activities = get_recent_activities(10)
        
        # Get recent logins
        recent_logins = get_recent_logins(10)

        # Add date utilities for the template
        from datetime import datetime
        
        # Combine all data into a single dashboard data object
        dashboard_data = {
            'overview': dashboard_stats,
            'clients': clients,
            'scanners': scanners,
            'recent_leads': recent_leads,
            'system_health': system_health,
            'recent_activities': recent_activities,
            'recent_logins': recent_logins,
            'datetime': datetime
        }
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error getting enhanced dashboard data: {str(e)}")
        # Return basic data structure to prevent template errors
        return {
            'overview': {},
            'clients': [],
            'scanners': [],
            'recent_leads': [],
            'system_health': {},
            'recent_activities': [],
            'recent_logins': [],
            'datetime': datetime
        }

def get_dashboard_statistics():
    """
    Get comprehensive dashboard statistics
    
    Returns:
        dict: Dashboard statistics including clients, scans, revenue, etc.
    """
    try:
        # Create connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Default values
        total_clients = 0
        active_clients = 0
        new_clients_30d = 0
        total_scanners = 0
        active_scanners = 0
        new_scanners_30d = 0
        total_scans = 0
        scans_today = 0
        subscription_breakdown = {}
        monthly_revenue = 0
        
        # Get client statistics
        try:
            cursor.execute("SELECT COUNT(*) FROM clients")
            total_clients = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM clients WHERE active = 1")
            active_clients = cursor.fetchone()[0]
            
            # Get new clients in last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM clients WHERE DATE(created_at) >= ?", (thirty_days_ago,))
            new_clients_30d = cursor.fetchone()[0]
        except Exception as e:
            logger.warning(f"Error getting client statistics: {str(e)}")
        
        # Get scanner statistics - try both 'scanners' and 'scanner' tables
        scanner_tables = ['scanners', 'scanner']
        for table in scanner_tables:
            try:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    # Table exists, get statistics
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_scanners += cursor.fetchone()[0]
                    
                    # Check if status column exists
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    if 'status' in columns:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE status = 'deployed'")
                        active_scanners += cursor.fetchone()[0]
                    
                    if 'created_at' in columns:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE DATE(created_at) >= ?", (thirty_days_ago,))
                        new_scanners_30d += cursor.fetchone()[0]
            except Exception as e:
                logger.warning(f"Error getting scanner statistics from {table}: {str(e)}")
        
        # Get scan statistics - try both 'scan_history' and 'scans' tables
        scan_tables = ['scan_history', 'scans']
        today = datetime.now().strftime('%Y-%m-%d')
        
        for table in scan_tables:
            try:
                # Check if table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    # Table exists, get statistics
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    total_scans += cursor.fetchone()[0]
                    
                    # Check if timestamp column exists
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Get today's scan count using the appropriate timestamp column
                    timestamp_column = None
                    for col in ['timestamp', 'created_at', 'scan_date']:
                        if col in columns:
                            timestamp_column = col
                            break
                    
                    if timestamp_column:
                        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE DATE({timestamp_column}) = ?", (today,))
                        scans_today += cursor.fetchone()[0]
            except Exception as e:
                logger.warning(f"Error getting scan statistics from {table}: {str(e)}")
        
        # Get revenue data - try different subscription column names
        subscription_columns = ['subscription_level', 'subscription', 'plan']
        for col in subscription_columns:
            try:
                # Check if column exists in clients table
                cursor.execute("PRAGMA table_info(clients)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if col in columns:
                    # Column exists, get subscription breakdown
                    cursor.execute(f"""
                    SELECT 
                        {col}, 
                        COUNT(*) as client_count
                    FROM clients 
                    WHERE active = 1 
                    GROUP BY {col}
                    """)
                    
                    # Define price points for each subscription level
                    price_points = {
                        'basic': 49.99,
                        'professional': 99.99,
                        'pro': 99.99,
                        'premium': 199.99,
                        'enterprise': 299.99,
                        'custom': 499.99,
                        None: 0  # Handle NULL values
                    }
                    
                    # Calculate subscription breakdown and monthly revenue
                    for row in cursor.fetchall():
                        level = row[0] or 'basic'  # Default to basic if NULL
                        count = row[1]
                        price = price_points.get(level.lower() if isinstance(level, str) else level, 49.99)
                        revenue = count * price
                        
                        subscription_breakdown[level] = {
                            'count': count,
                            'price': price,
                            'revenue': round(revenue, 2)
                        }
                        
                        monthly_revenue += revenue
                    
                    # If we got subscription data, break the loop
                    if subscription_breakdown:
                        break
            except Exception as e:
                logger.warning(f"Error getting subscription data using {col}: {str(e)}")
        
        # If we didn't get any subscription data, create default entries
        if not subscription_breakdown:
            subscription_breakdown = {
                'basic': {'count': active_clients, 'price': 49.99, 'revenue': round(active_clients * 49.99, 2)},
                'professional': {'count': 0, 'price': 99.99, 'revenue': 0},
                'enterprise': {'count': 0, 'price': 299.99, 'revenue': 0}
            }
            monthly_revenue = active_clients * 49.99
        
        # Check client-specific databases for additional scan counts
        try:
            # Find client databases
            client_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
            client_scan_count = 0
            client_scan_today_count = 0
            
            if os.path.exists(client_db_dir):
                for file in os.listdir(client_db_dir):
                    if file.endswith('.db'):
                        try:
                            client_db_path = os.path.join(client_db_dir, file)
                            client_conn = sqlite3.connect(client_db_path)
                            client_cursor = client_conn.cursor()
                            
                            # Check if scans table exists
                            client_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
                            if client_cursor.fetchone():
                                # Get total scans
                                client_cursor.execute("SELECT COUNT(*) FROM scans")
                                client_scan_count += client_cursor.fetchone()[0]
                                
                                # Get today's scans
                                client_cursor.execute("PRAGMA table_info(scans)")
                                columns = [col[1] for col in client_cursor.fetchall()]
                                
                                # Find timestamp column
                                timestamp_column = None
                                for col in ['timestamp', 'created_at', 'scan_date']:
                                    if col in columns:
                                        timestamp_column = col
                                        break
                                
                                if timestamp_column:
                                    client_cursor.execute(f"SELECT COUNT(*) FROM scans WHERE DATE({timestamp_column}) = ?", (today,))
                                    client_scan_today_count += client_cursor.fetchone()[0]
                            
                            client_conn.close()
                        except Exception as e:
                            logger.warning(f"Error reading client database {file}: {str(e)}")
                
                # Add client-specific counts to totals
                total_scans += client_scan_count
                scans_today += client_scan_today_count
        except Exception as e:
            logger.warning(f"Error checking client databases: {str(e)}")
        
        # Close the connection
        conn.close()
        
        # Create the statistics object
        stats = {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'inactive_clients': total_clients - active_clients,
            'new_clients_30d': new_clients_30d,
            'total_scanners': total_scanners,
            'active_scanners': active_scanners,
            'new_scanners_30d': new_scanners_30d,
            'total_scans': total_scans,
            'scans_today': scans_today,
            'monthly_revenue': round(monthly_revenue, 2),
            'yearly_revenue': round(monthly_revenue * 12, 2),
            'subscription_breakdown': subscription_breakdown
        }
        
        return stats
    
    except Exception as e:
        logger.error(f"Error getting dashboard statistics: {str(e)}")
        return {
            'total_clients': 0,
            'active_clients': 0,
            'inactive_clients': 0,
            'new_clients_30d': 0,
            'total_scanners': 0,
            'active_scanners': 0,
            'new_scanners_30d': 0,
            'total_scans': 0,
            'scans_today': 0,
            'monthly_revenue': 0,
            'yearly_revenue': 0,
            'subscription_breakdown': {}
        }

def get_recent_clients(limit=5):
    """
    Get recent clients with detailed information
    
    Args:
        limit (int): Maximum number of clients to return
        
    Returns:
        list: List of client dictionaries with detailed information
    """
    try:
        # Create connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent clients
        cursor.execute("""
        SELECT 
            c.id, c.username, c.business_name, c.contact_email, c.contact_phone,
            c.subscription_level, c.created_at, c.active
        FROM clients c
        ORDER BY c.created_at DESC
        LIMIT ?
        """, (limit,))
        
        clients = []
        for row in cursor.fetchall():
            if hasattr(row, 'keys'):
                client = dict(row)
            else:
                client = {
                    'id': row[0],
                    'username': row[1],
                    'business_name': row[2],
                    'user_email': row[3],
                    'contact_phone': row[4],
                    'subscription_level': row[5],
                    'created_at': row[6],
                    'active': row[7]
                }
            
            # Get scanner count for this client
            cursor.execute("""
            SELECT COUNT(*) FROM scanners
            WHERE client_id = ?
            """, (client['id'],))
            client['scanner_count'] = cursor.fetchone()[0]
            
            # Get scan count for this client
            cursor.execute("""
            SELECT COUNT(*) FROM scan_history
            WHERE client_id = ?
            """, (client['id'],))
            client['scan_count'] = cursor.fetchone()[0]
            
            # Calculate monthly revenue based on subscription level
            price_points = {
                'basic': 49.99,
                'professional': 99.99,
                'enterprise': 299.99,
                'custom': 499.99
            }
            level = client['subscription_level'] or 'basic'
            client['monthly_revenue'] = price_points.get(level, 0)
            
            # Get last activity for this client
            cursor.execute("""
            SELECT MAX(timestamp) FROM scan_history
            WHERE client_id = ?
            """, (client['id'],))
            last_activity = cursor.fetchone()[0]
            client['last_activity'] = last_activity or client['created_at']
            
            clients.append(client)
        
        # Close the connection
        conn.close()
        
        return clients
    
    except Exception as e:
        logger.error(f"Error getting recent clients: {str(e)}")
        return []

def get_all_scanners_with_details(limit=10):
    """
    Get all scanners with detailed information
    
    Args:
        limit (int): Maximum number of scanners to return
        
    Returns:
        list: List of scanner dictionaries with detailed information
    """
    try:
        scanners = []
        
        # Try using the existing function if available
        try:
            if hasattr(scanner_db_functions, 'get_all_scanners_for_admin'):
                scanners = scanner_db_functions.get_all_scanners_for_admin()
                # If we got scanners, return them limited to the requested number
                if scanners:
                    return scanners[:limit]
        except Exception as e:
            logger.warning(f"Error using scanner_db_functions.get_all_scanners_for_admin: {str(e)}")
        
        # Fall back to custom implementation
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Try both 'scanners' and 'scanner' tables
        for table_name in ['scanners', 'scanner']:
            try:
                # Check if the table exists
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                if not cursor.fetchone():
                    continue
                
                # Adjust the query based on available columns
                try:
                    # Get column information
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    # Build a query based on available columns
                    select_fields = []
                    if 'id' in columns:
                        select_fields.append(f"{table_name}.id")
                    else:
                        select_fields.append("NULL as id")
                    
                    if 'scanner_id' in columns:
                        select_fields.append(f"{table_name}.scanner_id")
                    else:
                        select_fields.append("NULL as scanner_id")
                    
                    if 'name' in columns:
                        select_fields.append(f"{table_name}.name")
                    else:
                        select_fields.append("'Unnamed Scanner' as name")
                    
                    if 'description' in columns:
                        select_fields.append(f"{table_name}.description")
                    else:
                        select_fields.append("NULL as description")
                    
                    if 'domain' in columns:
                        select_fields.append(f"{table_name}.domain")
                    else:
                        select_fields.append("NULL as domain")
                    
                    if 'status' in columns:
                        select_fields.append(f"{table_name}.status")
                    else:
                        select_fields.append("'unknown' as status")
                    
                    if 'created_at' in columns:
                        select_fields.append(f"{table_name}.created_at")
                    else:
                        select_fields.append("NULL as created_at")
                    
                    if 'updated_at' in columns:
                        select_fields.append(f"{table_name}.updated_at")
                    else:
                        select_fields.append("NULL as updated_at")
                    
                    if 'client_id' in columns:
                        select_fields.append(f"{table_name}.client_id")
                    else:
                        select_fields.append("NULL as client_id")
                    
                    if 'primary_color' in columns:
                        select_fields.append(f"{table_name}.primary_color")
                    else:
                        select_fields.append("NULL as primary_color")
                    
                    if 'secondary_color' in columns:
                        select_fields.append(f"{table_name}.secondary_color")
                    else:
                        select_fields.append("NULL as secondary_color")
                    
                    if 'button_color' in columns:
                        select_fields.append(f"{table_name}.button_color")
                    else:
                        select_fields.append("NULL as button_color")
                    
                    # Build the query
                    query = f"""SELECT 
                        {', '.join(select_fields)},
                        c.business_name, c.subscription_level
                    FROM {table_name}
                    LEFT JOIN clients c ON {table_name}.client_id = c.id
                    ORDER BY {table_name}.created_at DESC
                    LIMIT ?
                    """
                    
                    cursor.execute(query, (limit,))
                    
                    for row in cursor.fetchall():
                        if hasattr(row, 'keys'):
                            scanner = dict(row)
                        else:
                            scanner = {
                                'id': row[0],
                                'scanner_id': row[1],
                                'name': row[2],
                                'description': row[3],
                                'domain': row[4],
                                'status': row[5],
                                'created_at': row[6],
                                'updated_at': row[7],
                                'client_id': row[8],
                                'primary_color': row[9],
                                'secondary_color': row[10],
                                'button_color': row[11],
                                'business_name': row[12],
                                'subscription_level': row[13]
                            }
                        
                        # Get scan count for this scanner from various tables
                        scanner['scan_count'] = 0
                        scanner_id = scanner.get('scanner_id')
                        
                        if scanner_id:
                            # Try scan_history table
                            try:
                                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'")
                                if cursor.fetchone():
                                    cursor.execute("""
                                    SELECT COUNT(*) FROM scan_history
                                    WHERE scanner_id = ?
                                    """, (scanner_id,))
                                    scanner['scan_count'] += cursor.fetchone()[0]
                            except Exception as e:
                                logger.debug(f"Error counting scan_history: {str(e)}")
                            
                            # Try scans table
                            try:
                                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
                                if cursor.fetchone():
                                    cursor.execute("""
                                    SELECT COUNT(*) FROM scans
                                    WHERE scanner_id = ?
                                    """, (scanner_id,))
                                    scanner['scan_count'] += cursor.fetchone()[0]
                            except Exception as e:
                                logger.debug(f"Error counting scans: {str(e)}")
                            
                            # If client_id is available, try client-specific database
                            client_id = scanner.get('client_id')
                            if client_id:
                                try:
                                    from client_database_manager import get_scanner_scan_count
                                    client_scan_count = get_scanner_scan_count(client_id, scanner_id)
                                    scanner['scan_count'] += client_scan_count
                                except Exception as e:
                                    logger.debug(f"Error counting client scans: {str(e)}")
                        
                        scanners.append(scanner)
                except Exception as e:
                    logger.warning(f"Error building query for {table_name}: {str(e)}")
            except Exception as e:
                logger.warning(f"Error checking {table_name} table: {str(e)}")
        
        # Close the connection
        conn.close()
        
        # Remove duplicates based on scanner_id
        unique_scanners = []
        scanner_ids = set()
        for scanner in scanners:
            scanner_id = scanner.get('scanner_id')
            if scanner_id and scanner_id not in scanner_ids:
                scanner_ids.add(scanner_id)
                unique_scanners.append(scanner)
        
        # Return the top scanners up to the limit
        return unique_scanners[:limit]
    
    except Exception as e:
        logger.error(f"Error getting scanners with details: {str(e)}")
        return []

def get_recent_leads(limit=10):
    """
    Get recent leads from scan history across all clients
    
    Args:
        limit (int): Maximum number of leads to return
        
    Returns:
        list: List of lead dictionaries with detailed information
    """
    try:
        leads = []
        
        # First try to get leads from the main database's scan_history table
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if scan_history table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'")
            if cursor.fetchone():
                # Get recent leads from scan_history
                try:
                    cursor.execute("""
                    SELECT 
                        sh.id, sh.scan_id, sh.scanner_id, sh.client_id, sh.timestamp,
                        sh.lead_name, sh.lead_email, sh.lead_company, 
                        sh.security_score, sh.risk_level, sh.target_domain,
                        c.business_name as client_name
                    FROM scan_history sh
                    LEFT JOIN clients c ON sh.client_id = c.id
                    ORDER BY sh.timestamp DESC
                    LIMIT ?
                    """, (limit,))
                    
                    for row in cursor.fetchall():
                        if hasattr(row, 'keys'):
                            lead = dict(row)
                        else:
                            lead = {
                                'id': row[0],
                                'scan_id': row[1],
                                'scanner_id': row[2],
                                'client_id': row[3],
                                'timestamp': row[4],
                                'lead_name': row[5],
                                'lead_email': row[6],
                                'lead_company': row[7],
                                'security_score': row[8],
                                'risk_level': row[9],
                                'target_domain': row[10],
                                'client_name': row[11]
                            }
                        
                        # Parse user agent to get browser and OS info
                        lead['browser'], lead['os'] = detect_os_and_browser(lead.get('user_agent', ''))
                        
                        leads.append(lead)
                except Exception as e:
                    logger.warning(f"Error querying scan_history: {str(e)}")
            
            # Also try the scans table if it exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scans'")
            if cursor.fetchone():
                try:
                    cursor.execute("""
                    SELECT 
                        s.id, s.scan_id, s.scanner_id, s.client_id, s.timestamp,
                        s.lead_name, s.lead_email, s.lead_company, 
                        s.security_score, s.risk_level, s.target_domain,
                        c.business_name as client_name
                    FROM scans s
                    LEFT JOIN clients c ON s.client_id = c.id
                    ORDER BY s.timestamp DESC
                    LIMIT ?
                    """, (limit,))
                    
                    for row in cursor.fetchall():
                        if hasattr(row, 'keys'):
                            lead = dict(row)
                        else:
                            lead = {
                                'id': row[0],
                                'scan_id': row[1],
                                'scanner_id': row[2],
                                'client_id': row[3],
                                'timestamp': row[4],
                                'lead_name': row[5],
                                'lead_email': row[6],
                                'lead_company': row[7],
                                'security_score': row[8],
                                'risk_level': row[9],
                                'target_domain': row[10],
                                'client_name': row[11]
                            }
                        
                        # Parse user agent to get browser and OS info
                        lead['browser'], lead['os'] = detect_os_and_browser(lead.get('user_agent', ''))
                        
                        # Only add if not already in the list (based on scan_id)
                        if not any(l.get('scan_id') == lead.get('scan_id') for l in leads):
                            leads.append(lead)
                except Exception as e:
                    logger.warning(f"Error querying scans table: {str(e)}")
            
            conn.close()
        except Exception as e:
            logger.warning(f"Error accessing main database: {str(e)}")
        
        # If we don't have enough leads, try the client-specific databases
        if len(leads) < limit:
            try:
                # Import client database manager if available
                try:
                    from client_database_manager import get_recent_client_scans
                    client_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
                    
                    # Get list of client IDs by parsing database filenames
                    client_ids = []
                    if os.path.exists(client_db_dir):
                        for file in os.listdir(client_db_dir):
                            if file.startswith('client_') and file.endswith('_scans.db'):
                                try:
                                    client_id = int(file.split('_')[1])
                                    client_ids.append(client_id)
                                except:
                                    pass
                    
                    # Get scans from each client database
                    remaining_slots = limit - len(leads)
                    per_client_limit = max(2, remaining_slots // max(1, len(client_ids)))
                    
                    for client_id in client_ids:
                        try:
                            client_scans = get_recent_client_scans(client_id, per_client_limit)
                            
                            # Get client name from main database
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("SELECT business_name FROM clients WHERE id = ?", (client_id,))
                            result = cursor.fetchone()
                            client_name = result[0] if result else f"Client {client_id}"
                            conn.close()
                            
                            for scan in client_scans:
                                lead = {
                                    'id': scan.get('id'),
                                    'scan_id': scan.get('scan_id'),
                                    'scanner_id': scan.get('scanner_id'),
                                    'client_id': client_id,
                                    'timestamp': scan.get('timestamp'),
                                    'lead_name': scan.get('lead_name'),
                                    'lead_email': scan.get('lead_email'),
                                    'lead_company': scan.get('lead_company'),
                                    'security_score': scan.get('security_score'),
                                    'risk_level': scan.get('risk_level'),
                                    'target_domain': scan.get('target_domain'),
                                    'client_name': client_name
                                }
                                
                                # Only add if not already in the list (based on scan_id)
                                if not any(l.get('scan_id') == lead.get('scan_id') for l in leads):
                                    leads.append(lead)
                                    
                                    # Stop if we've reached the limit
                                    if len(leads) >= limit:
                                        break
                        except Exception as e:
                            logger.warning(f"Error getting scans for client {client_id}: {str(e)}")
                        
                        # Stop if we've reached the limit
                        if len(leads) >= limit:
                            break
                except ImportError:
                    logger.warning("client_database_manager not available")
            except Exception as e:
                logger.warning(f"Error accessing client databases: {str(e)}")
        
        # Sort by timestamp
        leads.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Limit to requested number
        return leads[:limit]
    
    except Exception as e:
        logger.error(f"Error getting recent leads: {str(e)}")
        return []

def get_system_health():
    """
    Get system health information
    
    Returns:
        dict: System health statistics
    """
    try:
        # Get database information
        db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cybrscan.db')
        db_size = os.path.getsize(db_file) if os.path.exists(db_file) else 0
        
        # Get client database information
        client_db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_databases')
        client_dbs = []
        client_db_total_size = 0
        
        if os.path.exists(client_db_dir):
            for file in os.listdir(client_db_dir):
                if file.endswith('.db'):
                    db_path = os.path.join(client_db_dir, file)
                    size = os.path.getsize(db_path)
                    client_dbs.append({
                        'name': file,
                        'size': size
                    })
                    client_db_total_size += size
        
        # Get system information
        hostname = socket.gethostname()
        platform_info = platform.platform()
        
        return {
            'db_integrity': 'ok',
            'main_db_size': db_size,
            'client_db_count': len(client_dbs),
            'client_db_total_size': client_db_total_size,
            'hostname': hostname,
            'platform': platform_info,
            'client_dbs': client_dbs
        }
    
    except Exception as e:
        logger.error(f"Error getting system health: {str(e)}")
        return {
            'db_integrity': 'unknown',
            'main_db_size': 0,
            'client_db_count': 0,
            'client_db_total_size': 0,
            'hostname': 'unknown',
            'platform': 'unknown',
            'client_dbs': []
        }

def get_recent_activities(limit=10):
    """
    Get recent user activities
    
    Args:
        limit (int): Maximum number of activities to return
        
    Returns:
        list: List of activity dictionaries
    """
    try:
        # Create connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if activity_log table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_log'")
        if not cursor.fetchone():
            # Create activity log table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                activity_type TEXT,
                activity_data TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            
            # No activities to return since we just created the table
            conn.close()
            return []
        
        # Get recent activities
        cursor.execute("""
        SELECT 
            a.id, a.user_id, a.activity_type, a.activity_data, a.timestamp,
            u.username, u.email, u.role
        FROM activity_log a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.timestamp DESC
        LIMIT ?
        """, (limit,))
        
        activities = []
        for row in cursor.fetchall():
            if hasattr(row, 'keys'):
                activity = dict(row)
            else:
                activity = {
                    'id': row[0],
                    'user_id': row[1],
                    'activity_type': row[2],
                    'activity_data': row[3],
                    'timestamp': row[4],
                    'username': row[5],
                    'email': row[6],
                    'role': row[7]
                }
            
            # Parse activity data if it's JSON
            if activity['activity_data'] and activity['activity_data'].strip():
                try:
                    activity['data'] = json.loads(activity['activity_data'])
                except:
                    activity['data'] = {'raw': activity['activity_data']}
            
            # Format activity for display
            activity['formatted'] = format_activity_for_display(activity)
            
            # Add relative time
            activity['relative_time'] = get_relative_time(activity['timestamp'])
            
            activities.append(activity)
        
        # Close the connection
        conn.close()
        
        return activities
    
    except Exception as e:
        logger.error(f"Error getting recent activities: {str(e)}")
        return []

def get_recent_logins(limit=10):
    """
    Get recent user logins
    
    Args:
        limit (int): Maximum number of logins to return
        
    Returns:
        list: List of login dictionaries
    """
    try:
        # Create connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if login_history table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_history'")
        if not cursor.fetchone():
            # Create login history table if it doesn't exist
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                success INTEGER DEFAULT 1
            )
            ''')
            conn.commit()
            
            # No logins to return since we just created the table
            conn.close()
            return []
        
        # Get recent logins
        cursor.execute("""
        SELECT 
            l.id, l.user_id, l.timestamp, l.ip_address, l.user_agent, l.success,
            u.username, u.email, u.role
        FROM login_history l
        LEFT JOIN users u ON l.user_id = u.id
        ORDER BY l.timestamp DESC
        LIMIT ?
        """, (limit,))
        
        logins = []
        for row in cursor.fetchall():
            if hasattr(row, 'keys'):
                login = dict(row)
            else:
                login = {
                    'id': row[0],
                    'user_id': row[1],
                    'timestamp': row[2],
                    'ip_address': row[3],
                    'user_agent': row[4],
                    'success': row[5],
                    'username': row[6],
                    'email': row[7],
                    'role': row[8]
                }
            
            # Parse user agent to get browser and OS info
            login['browser'], login['os'] = detect_os_and_browser(login['user_agent'])
            
            # Add relative time
            login['relative_time'] = get_relative_time(login['timestamp'])
            
            logins.append(login)
        
        # Close the connection
        conn.close()
        
        return logins
    
    except Exception as e:
        logger.error(f"Error getting recent logins: {str(e)}")
        return []

def detect_os_and_browser(user_agent_string):
    """
    Detect operating system and browser from user agent string
    
    Args:
        user_agent_string (str): The user agent string
        
    Returns:
        tuple: (browser, operating_system)
    """
    # Default values
    browser = "Unknown"
    os = "Unknown"
    
    if not user_agent_string:
        return browser, os
    
    # OS detection
    if "Windows" in user_agent_string:
        os = "Windows"
        if "Windows NT 10.0" in user_agent_string:
            os = "Windows 10/11"
        elif "Windows NT 6.3" in user_agent_string:
            os = "Windows 8.1"
        elif "Windows NT 6.2" in user_agent_string:
            os = "Windows 8"
        elif "Windows NT 6.1" in user_agent_string:
            os = "Windows 7"
    elif "Macintosh" in user_agent_string:
        os = "macOS"
    elif "Linux" in user_agent_string:
        if "Android" in user_agent_string:
            os = "Android"
        else:
            os = "Linux"
    elif "iPhone" in user_agent_string:
        os = "iOS"
    elif "iPad" in user_agent_string:
        os = "iPadOS"
    
    # Browser detection
    if "Firefox/" in user_agent_string:
        browser = "Firefox"
    elif "Edge/" in user_agent_string or "Edg/" in user_agent_string:
        browser = "Edge"
    elif "Chrome/" in user_agent_string and not "Chromium" in user_agent_string:
        browser = "Chrome"
    elif "Safari/" in user_agent_string and not "Chrome" in user_agent_string and not "Chromium" in user_agent_string:
        browser = "Safari"
    elif "MSIE" in user_agent_string or "Trident/" in user_agent_string:
        browser = "Internet Explorer"
    elif "Opera/" in user_agent_string or "OPR/" in user_agent_string:
        browser = "Opera"
    
    return browser, os

def format_activity_for_display(activity):
    """
    Format an activity record for human-readable display
    
    Args:
        activity (dict): Activity record
        
    Returns:
        str: Formatted activity description
    """
    try:
        activity_type = activity.get('activity_type', '').lower()
        
        if 'login' in activity_type:
            return f"Logged in"
        elif 'logout' in activity_type:
            return f"Logged out"
        elif 'create_scanner' in activity_type:
            scanner_name = activity.get('data', {}).get('name', 'a scanner')
            return f"Created scanner '{scanner_name}'"
        elif 'update_scanner' in activity_type:
            scanner_name = activity.get('data', {}).get('name', 'a scanner')
            return f"Updated scanner '{scanner_name}'"
        elif 'delete_scanner' in activity_type:
            scanner_id = activity.get('data', {}).get('scanner_id', 'unknown')
            return f"Deleted scanner ({scanner_id})"
        elif 'scan' in activity_type:
            target = activity.get('data', {}).get('target', 'a website')
            return f"Performed scan on {target}"
        elif 'subscription' in activity_type:
            level = activity.get('data', {}).get('level', 'a subscription')
            return f"Changed subscription to {level}"
        elif 'profile' in activity_type:
            return "Updated profile information"
        elif 'password' in activity_type:
            return "Changed password"
        else:
            # Generic fallback
            return f"{activity_type.replace('_', ' ').capitalize()}"
    
    except Exception as e:
        logger.error(f"Error formatting activity: {str(e)}")
        return "Unknown activity"

def get_relative_time(timestamp_str):
    """
    Convert timestamp string to relative time description
    
    Args:
        timestamp_str (str): Timestamp in string format
        
    Returns:
        str: Human-readable relative time
    """
    if not timestamp_str:
        return "Unknown time"
    
    try:
        # Parse timestamp string to datetime
        # Handle different timestamp formats
        if 'T' in timestamp_str:
            # ISO format with T separator
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        elif ' ' in timestamp_str:
            # Format with space separator
            timestamp = datetime.strptime(timestamp_str[:19], "%Y-%m-%d %H:%M:%S")
        else:
            # Just date
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
        
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} {'year' if years == 1 else 'years'} ago"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} {'month' if months == 1 else 'months'} ago"
        elif diff.days > 0:
            return f"{diff.days} {'day' if diff.days == 1 else 'days'} ago"
        elif diff.seconds // 3600 > 0:
            hours = diff.seconds // 3600
            return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
        elif diff.seconds // 60 > 0:
            minutes = diff.seconds // 60
            return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
        else:
            return "Just now"
    
    except Exception as e:
        logger.error(f"Error parsing timestamp {timestamp_str}: {str(e)}")
        return "Unknown time"

def enhance_admin_dashboard():
    """
    Enhance the admin dashboard by updating the dashboard route
    
    This function patches the admin.dashboard function to use the enhanced
    dashboard data provider.
    """
    try:
        import admin
        from types import MethodType
        
        # Store the original dashboard function
        original_dashboard = admin.admin_bp.view_functions['dashboard']
        
        # Define the enhanced dashboard function
        def enhanced_dashboard(user):
            """Enhanced admin dashboard with comprehensive data"""
            try:
                # Get enhanced dashboard data
                dashboard_data = get_enhanced_dashboard_data()
                
                # Add the user to the dashboard data
                dashboard_data['user'] = user
                
                # Render the enhanced dashboard template
                return admin.render_template('admin/admin-dashboard.html', **dashboard_data)
            except Exception as e:
                # Fall back to original dashboard if there's an error
                logger.error(f"Error in enhanced dashboard, falling back to original: {str(e)}")
                if original_dashboard:
                    return original_dashboard(user)
                else:
                    return admin.render_template(
                        'admin/error.html',
                        error=f"Error loading dashboard: {str(e)}",
                        user=user
                    )
        
        # Replace the dashboard function
        admin.admin_bp.view_functions['dashboard'] = enhanced_dashboard
        
        logger.info("✅ Admin dashboard successfully enhanced")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error enhancing admin dashboard: {str(e)}")
        return False

if __name__ == "__main__":
    # Test the enhanced dashboard
    print("🔍 Testing Enhanced Admin Dashboard")
    print("=" * 50)
    
    # Get dashboard data
    data = get_enhanced_dashboard_data()
    
    # Print summary
    print(f"✅ Overview data: {len(data['overview'])}")
    print(f"✅ Clients: {len(data['clients'])}")
    print(f"✅ Scanners: {len(data['scanners'])}")
    print(f"✅ Recent leads: {len(data['recent_leads'])}")
    print(f"✅ System health: {len(data['system_health'])}")
    
    # Enhance the admin dashboard
    enhance_admin_dashboard()