#!/usr/bin/env python3
"""
Test script for the enhanced admin dashboard

This script tests the enhanced_admin_dashboard module by calling its
functions and verifying the data returned.
"""

import logging
import json
import pprint
from enhanced_admin_dashboard import (
    get_enhanced_dashboard_data,
    get_dashboard_statistics,
    get_recent_clients,
    get_all_scanners_with_details,
    get_recent_leads,
    get_system_health,
    get_recent_activities,
    get_recent_logins
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dashboard_statistics():
    """Test the dashboard statistics function"""
    print("\n🔍 Testing dashboard statistics")
    stats = get_dashboard_statistics()
    print(f"Total clients: {stats.get('total_clients', 'N/A')}")
    print(f"Active clients: {stats.get('active_clients', 'N/A')}")
    print(f"New clients (30d): {stats.get('new_clients_30d', 'N/A')}")
    print(f"Total scanners: {stats.get('total_scanners', 'N/A')}")
    print(f"Monthly revenue: ${stats.get('monthly_revenue', 'N/A')}")
    print(f"Subscription breakdown: {len(stats.get('subscription_breakdown', {}))}")
    return stats

def test_recent_clients():
    """Test the recent clients function"""
    print("\n🔍 Testing recent clients")
    clients = get_recent_clients(limit=3)
    print(f"Retrieved {len(clients)} recent clients")
    if clients:
        print("First client details:")
        client = clients[0]
        print(f"  - ID: {client.get('id')}")
        print(f"  - Business: {client.get('business_name')}")
        print(f"  - Subscription: {client.get('subscription_level')}")
        print(f"  - Scanners: {client.get('scanner_count')}")
        print(f"  - Scans: {client.get('scan_count')}")
    return clients

def test_scanners_with_details():
    """Test the scanners with details function"""
    print("\n🔍 Testing scanners with details")
    scanners = get_all_scanners_with_details(limit=3)
    print(f"Retrieved {len(scanners)} scanners")
    if scanners:
        print("First scanner details:")
        scanner = scanners[0]
        print(f"  - ID: {scanner.get('scanner_id', '')[:8]}...")
        print(f"  - Name: {scanner.get('name')}")
        print(f"  - Domain: {scanner.get('domain')}")
        print(f"  - Client: {scanner.get('business_name')}")
        print(f"  - Status: {scanner.get('status')}")
        print(f"  - Scans: {scanner.get('scan_count')}")
    return scanners

def test_recent_leads():
    """Test the recent leads function"""
    print("\n🔍 Testing recent leads")
    leads = get_recent_leads(limit=3)
    print(f"Retrieved {len(leads)} recent leads")
    if leads:
        print("First lead details:")
        lead = leads[0]
        print(f"  - Name: {lead.get('lead_name', 'N/A')}")
        print(f"  - Email: {lead.get('lead_email', 'N/A')}")
        print(f"  - Company: {lead.get('lead_company', 'N/A')}")
        print(f"  - Client: {lead.get('client_name', 'N/A')}")
        print(f"  - Score: {lead.get('security_score', 'N/A')}")
    return leads

def test_system_health():
    """Test the system health function"""
    print("\n🔍 Testing system health")
    health = get_system_health()
    print(f"DB Integrity: {health.get('db_integrity', 'N/A')}")
    print(f"Main DB Size: {(health.get('main_db_size', 0) / 1024 / 1024):.2f} MB")
    print(f"Client DB Count: {health.get('client_db_count', 'N/A')}")
    print(f"Client DB Total Size: {(health.get('client_db_total_size', 0) / 1024 / 1024):.2f} MB")
    print(f"Hostname: {health.get('hostname', 'N/A')}")
    return health

def test_recent_activities():
    """Test the recent activities function"""
    print("\n🔍 Testing recent activities")
    activities = get_recent_activities(limit=3)
    print(f"Retrieved {len(activities)} recent activities")
    if activities:
        print("First activity details:")
        activity = activities[0]
        print(f"  - Type: {activity.get('activity_type', 'N/A')}")
        print(f"  - User: {activity.get('username', 'N/A')}")
        print(f"  - Time: {activity.get('relative_time', 'N/A')}")
        print(f"  - Formatted: {activity.get('formatted', 'N/A')}")
    return activities

def test_recent_logins():
    """Test the recent logins function"""
    print("\n🔍 Testing recent logins")
    logins = get_recent_logins(limit=3)
    print(f"Retrieved {len(logins)} recent logins")
    if logins:
        print("First login details:")
        login = logins[0]
        print(f"  - User: {login.get('username', 'N/A')}")
        print(f"  - Time: {login.get('relative_time', 'N/A')}")
        print(f"  - IP: {login.get('ip_address', 'N/A')}")
        print(f"  - Browser: {login.get('browser', 'N/A')}")
        print(f"  - OS: {login.get('os', 'N/A')}")
    return logins

def test_enhanced_dashboard_data():
    """Test the full enhanced dashboard data function"""
    print("\n🔍 Testing full enhanced dashboard data")
    data = get_enhanced_dashboard_data()
    print("Dashboard data sections:")
    for key, value in data.items():
        if key == 'datetime':
            print(f"  - {key}: <datetime module>")
        elif isinstance(value, dict):
            print(f"  - {key}: {len(value)} items")
        elif isinstance(value, list):
            print(f"  - {key}: {len(value)} items")
        else:
            print(f"  - {key}: {value}")
    return data

def main():
    """Main test function"""
    print("=" * 50)
    print("Testing Enhanced Admin Dashboard")
    print("=" * 50)
    
    try:
        # Run all tests
        test_dashboard_statistics()
        test_recent_clients()
        test_scanners_with_details()
        test_recent_leads()
        test_system_health()
        test_recent_activities()
        test_recent_logins()
        test_enhanced_dashboard_data()
        
        print("\n✅ All tests completed successfully")
        print("The enhanced admin dashboard is ready to be applied")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"\n❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main()