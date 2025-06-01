#!/usr/bin/env python3
"""
Test script to verify the enhanced scan data processing for port scan results and OS information
"""

import json
import sys
import os

# Test data - a scan with network findings and user agent
test_scan = {
    "scan_id": "test_scan_1",
    "timestamp": "2025-05-29 12:34:56",
    "email": "test@example.com",
    "client_info": {
        "name": "Test User",
        "company": "Test Company"
    },
    "target": "example.com",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "network": [
        ("Port 80 is open (HTTP)", "Medium"),
        ("Port 443 is open (HTTPS)", "Low"),
        ("Port 22 is open (SSH)", "High"),
        ("Port 21 is open (FTP)", "Critical"),
        ("Port 3389 is open (RDP)", "High")
    ],
    "risk_assessment": 65
}

def main():
    # Add current directory to path so we can import from current files
    sys.path.append(os.getcwd())
    
    try:
        # Try to import the format_scan_results_for_client function
        print("Attempting to import format_scan_results_for_client...")
        
        # Try to import from client_db first (CybrScann-main)
        try:
            from client_db import format_scan_results_for_client, detect_os_and_browser, get_risk_level
            print("✅ Successfully imported from client_db")
        except ImportError:
            # Fall back to client.py (CybrScan_1)
            try:
                from client import process_scan_data as format_scan_results_for_client
                from client import detect_os_and_browser, get_risk_level
                print("✅ Successfully imported from client")
            except ImportError:
                print("❌ Failed to import required functions")
                return
        
        # Process the test scan data
        print("\nProcessing test scan data...")
        formatted_scan = format_scan_results_for_client(test_scan)
        
        # Check if formatted_scan was returned
        if not formatted_scan:
            print("❌ format_scan_results_for_client returned empty result")
            return
        
        # Check network data processing
        print("\nChecking network data processing:")
        if 'network' in formatted_scan and 'open_ports' in formatted_scan['network']:
            open_ports = formatted_scan['network']['open_ports']
            print(f"✅ Open ports detected: {open_ports['count']}")
            print(f"✅ Port list: {open_ports['list']}")
            print(f"✅ Port severity: {open_ports['severity']}")
        else:
            print("❌ Missing network data or open_ports section")
        
        # Check OS and browser detection
        print("\nChecking OS and browser detection:")
        if 'client_info' in formatted_scan:
            client_info = formatted_scan['client_info']
            print(f"✅ OS detected: {client_info.get('os', 'Missing')}")
            print(f"✅ Browser detected: {client_info.get('browser', 'Missing')}")
        else:
            print("❌ Missing client_info section")
        
        # Check risk assessment formatting
        print("\nChecking risk assessment formatting:")
        if 'risk_assessment' in formatted_scan and isinstance(formatted_scan['risk_assessment'], dict):
            risk = formatted_scan['risk_assessment']
            print(f"✅ Risk score: {risk.get('overall_score', 'Missing')}")
            print(f"✅ Risk level: {risk.get('risk_level', 'Missing')}")
            print(f"✅ Risk color: {risk.get('color', 'Missing')}")
        else:
            print("❌ Missing or improperly formatted risk_assessment section")
        
        # Print the full formatted scan for inspection
        print("\nFull formatted scan data:")
        print(json.dumps(formatted_scan, indent=2))
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    main()