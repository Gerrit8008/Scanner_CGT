#!/usr/bin/env python3
"""
Script to enhance scan data processing in CybrScann-main to properly display port scan results and OS information
"""

import os
import re
import json

def update_format_scan_results_for_client():
    """
    Update the format_scan_results_for_client function in client_db.py to better handle
    port scan and OS information, similar to the process_scan_data function in CybrScan_1
    """
    client_db_path = 'client_db.py'
    
    # Read the file content
    with open(client_db_path, 'r') as f:
        content = f.read()
    
    # Look for the format_scan_results_for_client function
    function_pattern = r'def format_scan_results_for_client\(.*?\):.*?return scan_data'
    function_match = re.search(function_pattern, content, re.DOTALL)
    
    if function_match:
        # Get the original function content
        original_function = function_match.group(0)
        
        # Create the enhanced function
        enhanced_function = """def format_scan_results_for_client(scan_data):
    """Format scan results for client-friendly display"""
    try:
        if not scan_data:
            return None
        
        # Add client-friendly formatting
        formatted_scan = scan_data.copy()
        
        # Parse scan_results if it exists as a string
        if 'scan_results' in formatted_scan and isinstance(formatted_scan['scan_results'], str):
            try:
                parsed_results = json.loads(formatted_scan['scan_results'])
                if isinstance(parsed_results, dict):
                    # Merge parsed results with formatted_scan, but don't overwrite existing keys
                    for key, value in parsed_results.items():
                        if key not in formatted_scan:
                            formatted_scan[key] = value
            except Exception as e:
                logging.error(f"Error parsing scan_results JSON: {e}")
        
        # Ensure 'network' section exists with open_ports data
        if 'network' not in formatted_scan:
            formatted_scan['network'] = {}
        
        # Ensure open_ports structure exists
        if 'open_ports' not in formatted_scan['network']:
            # Check if 'network' is a list of findings
            if isinstance(formatted_scan['network'], list):
                # Extract port information from network findings
                port_list = []
                port_details = []
                
                for finding in formatted_scan['network']:
                    if isinstance(finding, tuple) and len(finding) >= 2:
                        message, severity = finding
                        # Extract port info if this is a port finding
                        if 'Port ' in message and ' is open' in message:
                            try:
                                port_match = re.search(r'Port (\\d+)', message)
                                if port_match:
                                    port_num = int(port_match.group(1))
                                    service = "Unknown"
                                    # Try to extract service name if in parentheses
                                    service_match = re.search(r'\\((.*?)\\)', message)
                                    if service_match:
                                        service = service_match.group(1)
                                    
                                    port_list.append(port_num)
                                    port_details.append({
                                        'port': port_num,
                                        'service': service,
                                        'severity': severity
                                    })
                            except Exception as e:
                                logging.error(f"Error parsing port information: {e}")
                
                # Create structured open_ports data
                formatted_scan['network'] = {
                    'scan_results': formatted_scan['network'],  # Keep original findings
                    'open_ports': {
                        'count': len(port_list),
                        'list': port_list,
                        'details': port_details,
                        'severity': 'High' if len(port_list) > 5 else 'Medium' if len(port_list) > 2 else 'Low'
                    }
                }
            else:
                # Just ensure the structure exists
                formatted_scan['network']['open_ports'] = {
                    'count': 0,
                    'list': [],
                    'details': [],
                    'severity': 'Low'
                }
        
        # Ensure client_info section exists
        if 'client_info' not in formatted_scan:
            formatted_scan['client_info'] = {}
        
        # Add OS and browser info if missing
        if ('os' not in formatted_scan['client_info'] or 'browser' not in formatted_scan['client_info']) and 'user_agent' in formatted_scan:
            # Detect OS and browser from user agent
            user_agent = formatted_scan.get('user_agent', '')
            os_info, browser_info = detect_os_and_browser(user_agent)
            
            if 'os' not in formatted_scan['client_info'] or not formatted_scan['client_info']['os'] or formatted_scan['client_info']['os'] == 'N/A':
                formatted_scan['client_info']['os'] = os_info
            
            if 'browser' not in formatted_scan['client_info'] or not formatted_scan['client_info']['browser'] or formatted_scan['client_info']['browser'] == 'N/A':
                formatted_scan['client_info']['browser'] = browser_info
        
        # Format risk levels
        if 'risk_assessment' in formatted_scan:
            # If risk_assessment is just a score, convert to proper structure
            if isinstance(formatted_scan['risk_assessment'], (int, float, str)):
                try:
                    score = float(formatted_scan['risk_assessment'])
                    formatted_scan['risk_assessment'] = {
                        'overall_score': score,
                        'risk_level': get_risk_level(score),
                        'color': get_color_for_score(score)
                    }
                except:
                    # Keep as is if we can't convert
                    pass
            elif isinstance(formatted_scan['risk_assessment'], dict):
                # Ensure required fields exist
                risk_assessment = formatted_scan['risk_assessment']
                
                # Add risk level text if missing
                if 'risk_level' not in risk_assessment and 'overall_score' in risk_assessment:
                    score = risk_assessment['overall_score']
                    risk_assessment['risk_level'] = get_risk_level(score)
                
                # Add color if missing
                if 'color' not in risk_assessment and 'overall_score' in risk_assessment:
                    score = risk_assessment['overall_score']
                    risk_assessment['color'] = get_color_for_score(score)
                
                # Store back
                formatted_scan['risk_assessment'] = risk_assessment
                
                # Update color for display
                risk_level = formatted_scan['risk_assessment'].get('risk_level', 'Unknown')
                if risk_level.lower() == 'critical':
                    formatted_scan['risk_color'] = 'danger'
                elif risk_level.lower() == 'high':
                    formatted_scan['risk_color'] = 'warning'
                elif risk_level.lower() == 'medium':
                    formatted_scan['risk_color'] = 'info'
                else:
                    formatted_scan['risk_color'] = 'success'
        
        # Format dates for display
        if 'timestamp' in formatted_scan and not formatted_scan.get('formatted_date'):
            try:
                from datetime import datetime
                if isinstance(formatted_scan['timestamp'], str):
                    # Handle different date formats
                    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            timestamp = datetime.strptime(formatted_scan['timestamp'], fmt)
                            formatted_scan['formatted_date'] = timestamp.strftime('%B %d, %Y')
                            formatted_scan['formatted_time'] = timestamp.strftime('%I:%M %p')
                            break
                        except ValueError:
                            continue
            except Exception as e:
                logging.error(f"Error formatting timestamp: {e}")
        
        # Add summary statistics
        if 'risk_assessment' in formatted_scan:
            risk_assessment = formatted_scan['risk_assessment']
            formatted_scan['total_issues'] = (
                risk_assessment.get('critical_issues', 0) +
                risk_assessment.get('high_issues', 0) +
                risk_assessment.get('medium_issues', 0) +
                risk_assessment.get('low_issues', 0)
            )
        
        return formatted_scan
    except Exception as e:
        logging.error(f"Error formatting scan results: {e}")
        return scan_data"""
        
        # Replace the original function with the enhanced one
        content = content.replace(original_function, enhanced_function)
        
        # Add helper functions if they don't exist
        if "def detect_os_and_browser" not in content:
            detect_os_function = """
def detect_os_and_browser(user_agent):
    """Detect OS and browser from user agent string"""
    os_info = "Unknown"
    browser_info = "Unknown"
    
    if not user_agent:
        return os_info, browser_info
    
    # Detect OS
    if "Windows" in user_agent:
        if "Windows NT 10" in user_agent:
            os_info = "Windows 10/11"
        elif "Windows NT 6.3" in user_agent:
            os_info = "Windows 8.1"
        elif "Windows NT 6.2" in user_agent:
            os_info = "Windows 8"
        elif "Windows NT 6.1" in user_agent:
            os_info = "Windows 7"
        elif "Windows NT 6.0" in user_agent:
            os_info = "Windows Vista"
        elif "Windows NT 5.1" in user_agent:
            os_info = "Windows XP"
        else:
            os_info = "Windows"
    elif "Mac OS X" in user_agent:
        if "iPhone" in user_agent or "iPad" in user_agent:
            os_info = "iOS"
        else:
            os_info = "macOS"
    elif "Linux" in user_agent:
        if "Android" in user_agent:
            os_info = "Android"
        else:
            os_info = "Linux"
    elif "FreeBSD" in user_agent:
        os_info = "FreeBSD"
    
    # Detect browser
    if "Firefox/" in user_agent:
        browser_info = "Firefox"
    elif "Edge/" in user_agent or "Edg/" in user_agent:
        browser_info = "Edge"
    elif "Chrome/" in user_agent and "Chromium" not in user_agent and "Edge" not in user_agent and "Edg/" not in user_agent:
        browser_info = "Chrome"
    elif "Safari/" in user_agent and "Chrome" not in user_agent and "Edge" not in user_agent:
        browser_info = "Safari"
    elif "MSIE" in user_agent or "Trident/" in user_agent:
        browser_info = "Internet Explorer"
    elif "Opera/" in user_agent or "OPR/" in user_agent:
        browser_info = "Opera"
    
    return os_info, browser_info"""
            
            # Add the function after the imports
            import_section_end = content.find("CLIENT_DB_PATH")
            if import_section_end > 0:
                content = content[:import_section_end] + detect_os_function + "\n\n" + content[import_section_end:]
        
        # Add get_risk_level and get_color_for_score functions if they don't exist
        if "def get_risk_level" not in content:
            risk_level_function = """
def get_risk_level(score):
    """Get risk level text based on score"""
    if score >= 90:
        return 'Low'
    elif score >= 80:
        return 'Low-Medium'
    elif score >= 70:
        return 'Medium'
    elif score >= 60:
        return 'Medium-High'
    elif score >= 50:
        return 'High'
    else:
        return 'Critical'

def get_color_for_score(score):
    """Get color for a risk score"""
    if score >= 90:
        return '#28a745'  # Green (low risk)
    elif score >= 70:
        return '#17a2b8'  # Blue (medium risk)
    elif score >= 50:
        return '#ffc107'  # Yellow (high risk)
    else:
        return '#dc3545'  # Red (critical risk)"""
            
            # Add the functions after the imports or after detect_os_and_browser
            import_section_end = content.find("CLIENT_DB_PATH")
            if import_section_end > 0:
                content = content[:import_section_end] + risk_level_function + "\n\n" + content[import_section_end:]
        
        # Ensure required imports are present
        if "import re" not in content:
            content = content.replace("import json", "import json\nimport re")
        
        # Write the updated content back to the file
        with open(client_db_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Successfully updated format_scan_results_for_client function in {client_db_path}")
    else:
        print(f"❌ Could not find format_scan_results_for_client function in {client_db_path}")

def update_client_report_view():
    """
    Update the report_view function in client.py to ensure it properly processes scan data
    """
    client_path = 'client.py'
    
    with open(client_path, 'r') as f:
        content = f.read()
    
    # Find the report_view function
    report_view_pattern = r'@client_bp\.route\(\'/reports/(?P<scan_id>.*?)\'\).*?def report_view.*?return render_template\('
    report_view_match = re.search(report_view_pattern, content, re.DOTALL)
    
    if report_view_match:
        # Check if format_scan_results_for_client is already called
        if "formatted_scan = format_scan_results_for_client" in report_view_match.group(0):
            print(f"✅ report_view function in {client_path} already calls format_scan_results_for_client")
            return
        
        # Find where scan is fetched
        get_scan_pattern = r'scan = get_scan_results\(scan_id\)'
        get_scan_match = re.search(get_scan_pattern, content)
        
        if get_scan_match:
            # Add formatting call after getting scan results
            format_code = """
        # Format scan results for client-friendly display with enhanced port scan and OS info
        formatted_scan = format_scan_results_for_client(scan)
"""
            content = content.replace(get_scan_match.group(0), get_scan_match.group(0) + format_code)
            
            # Update the render_template call to use formatted_scan
            content = content.replace("scan=scan", "scan=formatted_scan or scan")
            
            # Write the updated content
            with open(client_path, 'w') as f:
                f.write(content)
            
            print(f"✅ Successfully updated report_view function in {client_path} to use format_scan_results_for_client")
        else:
            print(f"❌ Could not find get_scan_results call in report_view function")
    else:
        print(f"❌ Could not find report_view function in {client_path}")

def main():
    """Main function to update scan data processing"""
    print("Updating scan data processing to properly display port scan results and OS information...")
    
    # Update the format_scan_results_for_client function
    update_format_scan_results_for_client()
    
    # Update client.py report_view function
    update_client_report_view()
    
    print("\nDone! Scan data processing has been updated to properly display port scan results and OS information.")
    print("Changes made:")
    print("1. Enhanced format_scan_results_for_client function to process port scan data and OS information")
    print("2. Added helper functions for OS detection and risk level calculation")
    print("3. Updated report_view function to use the enhanced formatting")
    print("\nTo make the changes effective, please restart the application server.")

if __name__ == "__main__":
    main()