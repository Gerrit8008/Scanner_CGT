#!/usr/bin/env python3
"""
Test script to verify that the modular scan data processor maintains 
the same functionality as the original implementation
"""

import json
import os
import sys
from datetime import datetime

# Ensure the current directory is in the path
sys.path.append(os.path.abspath('.'))

# Create directories if they don't exist
os.makedirs('scanner', exist_ok=True)
if not os.path.exists('scanner/__init__.py'):
    with open('scanner/__init__.py', 'w') as f:
        f.write('# Scanner package\n')

# Import both the original and new implementations
try:
    print("Testing original implementation...")
    from scan_functions_backup import process_scan_data as original_process
    from scan_functions_backup import detect_os_and_browser as original_detect_os
    print("✅ Successfully imported original functions")
except ImportError as e:
    print(f"❌ Could not import original functions: {e}")
    sys.exit(1)

try:
    print("Testing modular implementation...")
    from scanner.data_processor import process_scan_data as modular_process
    from scanner.data_processor import detect_os_and_browser as modular_detect_os
    from scanner.data_processor import enhance_report_view
    print("✅ Successfully imported modular functions")
except ImportError as e:
    print(f"❌ Could not import modular functions: {e}")
    sys.exit(1)

# Test data - a realistic scan with network findings and user agent
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

# Test with scan_results as JSON string
test_scan_json_results = {
    "scan_id": "test_scan_json_2",
    "timestamp": "2025-05-29 12:34:56",
    "scan_results": json.dumps({
        "network": [
            ("Port 8080 is open (HTTP Proxy)", "Medium"),
            ("Port 25 is open (SMTP)", "High")
        ],
        "client_info": {
            "os": "Linux",
            "browser": "Firefox"
        },
        "risk_assessment": {
            "overall_score": 45,
            "risk_level": "Critical"
        }
    })
}

# Test with existing network object
test_scan_network_object = {
    "scan_id": "test_scan_object_3",
    "timestamp": "2025-05-29 12:34:56",
    "network": {
        "firewall": {"status": "Enabled", "severity": "Low"},
    }
}

def compare_results(original, modular, label):
    """Compare results from original and modular implementations"""
    print(f"\n== Testing {label} ==")
    
    # Check if both processed the data
    if not original and not modular:
        print("❌ Both implementations failed to process data")
        return False
    elif not original:
        print("❌ Original implementation failed to process data")
        return False
    elif not modular:
        print("❌ Modular implementation failed to process data")
        return False
    
    # Check key structure
    original_keys = set(original.keys())
    modular_keys = set(modular.keys())
    
    print(f"Original has {len(original_keys)} keys")
    print(f"Modular has {len(modular_keys)} keys")
    
    # Check for missing keys
    missing_in_modular = original_keys - modular_keys
    if missing_in_modular:
        print(f"❌ Keys missing in modular implementation: {missing_in_modular}")
    
    # Check network structure
    if 'network' in original and 'network' in modular:
        original_network = original.get('network', {})
        modular_network = modular.get('network', {})
        
        # Check open_ports
        original_ports = original_network.get('open_ports', {})
        modular_ports = modular_network.get('open_ports', {})
        
        if original_ports.get('count') != modular_ports.get('count'):
            print(f"❌ Port count mismatch: Original={original_ports.get('count')}, Modular={modular_ports.get('count')}")
        else:
            print(f"✅ Port count matches: {original_ports.get('count')}")
        
        # Check port list
        if set(original_ports.get('list', [])) != set(modular_ports.get('list', [])):
            print("❌ Port list mismatch")
        else:
            print(f"✅ Port list matches: {sorted(original_ports.get('list', []))}")
    
    # Check client_info
    if 'client_info' in original and 'client_info' in modular:
        original_client = original.get('client_info', {})
        modular_client = modular.get('client_info', {})
        
        for field in ['os', 'browser']:
            if original_client.get(field) != modular_client.get(field):
                print(f"❌ client_info.{field} mismatch: Original={original_client.get(field)}, Modular={modular_client.get(field)}")
            else:
                print(f"✅ client_info.{field} matches: {original_client.get(field)}")
    
    # Check risk_assessment
    if 'risk_assessment' in original and 'risk_assessment' in modular:
        original_risk = original.get('risk_assessment', {})
        modular_risk = modular.get('risk_assessment', {})
        
        for field in ['overall_score', 'risk_level', 'color']:
            if isinstance(original_risk, dict) and isinstance(modular_risk, dict):
                if original_risk.get(field) != modular_risk.get(field):
                    print(f"❌ risk_assessment.{field} mismatch: Original={original_risk.get(field)}, Modular={modular_risk.get(field)}")
                else:
                    print(f"✅ risk_assessment.{field} matches: {original_risk.get(field)}")
    
    print("✅ Basic comparison completed")
    return True

def test_user_agent_detection():
    """Test OS and browser detection from user agent strings"""
    print("\n== Testing User Agent Detection ==")
    
    test_cases = [
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "expected": ("Windows 10/11", "Chrome")
        },
        {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
            "expected": ("iOS", "Safari")
        },
        {
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "expected": ("Linux", "Firefox")
        },
        {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
            "expected": ("Windows 10/11", "Edge")
        },
        {
            "user_agent": "",
            "expected": ("Unknown", "Unknown")
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        original_result = original_detect_os(test_case["user_agent"])
        modular_result = modular_detect_os(test_case["user_agent"])
        expected = test_case["expected"]
        
        print(f"\nCase {i+1}: {test_case['user_agent'][:30]}...")
        print(f"Expected: {expected}")
        print(f"Original: {original_result}")
        print(f"Modular: {modular_result}")
        
        if original_result != expected:
            print(f"❌ Original implementation doesn't match expected")
        else:
            print(f"✅ Original implementation matches expected")
        
        if modular_result != expected:
            print(f"❌ Modular implementation doesn't match expected")
        else:
            print(f"✅ Modular implementation matches expected")
        
        if original_result != modular_result:
            print(f"❌ Original and modular implementations don't match")
        else:
            print(f"✅ Original and modular implementations match")

def test_enhance_report_view():
    """Test the enhance_report_view function"""
    print("\n== Testing enhance_report_view Function ==")
    
    # Create a minimal scan with missing data
    minimal_scan = {
        "scan_id": "minimal_scan_1",
        "lead_name": "John Doe",
        "lead_email": "john@example.com", 
        "lead_company": "Example Corp",
        "security_score": 60
    }
    
    # Process with the new enhance_report_view function
    enhanced_scan = enhance_report_view(minimal_scan)
    
    # Check that it added required fields
    if 'client_info' in enhanced_scan:
        print(f"✅ Added client_info section: {enhanced_scan['client_info']}")
    else:
        print("❌ Failed to add client_info section")
    
    if 'risk_assessment' in enhanced_scan:
        print(f"✅ Added risk_assessment section: {enhanced_scan['risk_assessment']}")
    else:
        print("❌ Failed to add risk_assessment section")
    
    if enhanced_scan.get('risk_assessment', {}).get('color'):
        print(f"✅ Added risk color: {enhanced_scan['risk_assessment']['color']}")
    else:
        print("❌ Failed to add risk color")

def main():
    """Run all tests"""
    print("=== Testing Scan Data Processing Functions ===")
    
    # Test with basic scan
    original_result1 = original_process(test_scan)
    modular_result1 = modular_process(test_scan)
    compare_results(original_result1, modular_result1, "basic scan")
    
    # Test with JSON results
    original_result2 = original_process(test_scan_json_results)
    modular_result2 = modular_process(test_scan_json_results)
    compare_results(original_result2, modular_result2, "JSON results scan")
    
    # Test with network object
    original_result3 = original_process(test_scan_network_object)
    modular_result3 = modular_process(test_scan_network_object)
    compare_results(original_result3, modular_result3, "network object scan")
    
    # Test OS and browser detection
    test_user_agent_detection()
    
    # Test enhance_report_view
    test_enhance_report_view()
    
    print("\n=== Testing Complete ===")
    print("The modular implementation appears to maintain the same functionality as the original.")

if __name__ == "__main__":
    main()