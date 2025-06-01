#!/usr/bin/env python3
"""
Backup of critical scan report processing functions from CybrScann-main

This file contains copies of the key functions that handle scan processing 
and report generation in the CybrScann-main codebase. It serves as a 
reference and backup to ensure functionality is maintained during refactoring.
"""

import re
import json
import logging
from datetime import datetime

def process_scan_data(scan):
    '''Process and enhance scan data for display'''
    if not scan:
        return {}
    
    # Handle string JSON data
    if isinstance(scan, str):
        try:
            scan_data = json.loads(scan)
        except:
            return {}
    else:
        # Make a copy to avoid modifying the original
        if hasattr(scan, 'get'):  # dict-like object
            scan_data = dict(scan)
        else:
            return scan  # Can't process
    
    # Parse scan_results if it exists
    if scan_data.get('scan_results') and isinstance(scan_data['scan_results'], str):
        try:
            parsed_results = json.loads(scan_data['scan_results'])
            if isinstance(parsed_results, dict):
                # Merge parsed results with scan_data, but don't overwrite existing keys
                for key, value in parsed_results.items():
                    if key not in scan_data:
                        scan_data[key] = value
        except:
            pass  # Failed to parse scan_results
    
    # Ensure 'network' section exists with open_ports data
    if 'network' not in scan_data:
        scan_data['network'] = {}
    
    # Ensure open_ports structure exists
    if 'open_ports' not in scan_data['network']:
        # Check if 'network' is a list of findings
        if isinstance(scan_data['network'], list):
            # Extract port information from network findings
            port_list = []
            port_details = []
            
            for finding in scan_data['network']:
                if isinstance(finding, tuple) and len(finding) >= 2:
                    message, severity = finding
                    # Extract port info if this is a port finding
                    if 'Port ' in message and ' is open' in message:
                        try:
                            port_match = re.search(r'Port (\d+)', message)
                            if port_match:
                                port_num = int(port_match.group(1))
                                service = "Unknown"
                                # Try to extract service name if in parentheses
                                service_match = re.search(r'\((.*?)\)', message)
                                if service_match:
                                    service = service_match.group(1)
                                
                                port_list.append(port_num)
                                port_details.append({
                                    'port': port_num,
                                    'service': service,
                                    'severity': severity
                                })
                        except Exception as e:
                            pass  # Skip this finding if we can't parse it
            
            # Create structured open_ports data
            scan_data['network'] = {
                'scan_results': scan_data['network'],  # Keep original findings
                'open_ports': {
                    'count': len(port_list),
                    'list': port_list,
                    'details': port_details,
                    'severity': 'High' if len(port_list) > 5 else 'Medium' if len(port_list) > 2 else 'Low'
                }
            }
        else:
            # Just ensure the structure exists
            scan_data['network']['open_ports'] = {
                'count': 0,
                'list': [],
                'details': [],
                'severity': 'Low'
            }
    
    # Ensure client_info section exists
    if 'client_info' not in scan_data:
        scan_data['client_info'] = {}
    
    # Add OS and browser info if missing
    if ('os' not in scan_data['client_info'] or 'browser' not in scan_data['client_info']) and 'user_agent' in scan_data:
        # Detect OS and browser from user agent
        user_agent = scan_data.get('user_agent', '')
        os_info, browser_info = detect_os_and_browser(user_agent)
        
        if 'os' not in scan_data['client_info'] or not scan_data['client_info']['os']:
            scan_data['client_info']['os'] = os_info
        
        if 'browser' not in scan_data['client_info'] or not scan_data['client_info']['browser']:
            scan_data['client_info']['browser'] = browser_info
    
    # Ensure risk_assessment section has proper formatting
    if 'risk_assessment' in scan_data:
        if isinstance(scan_data['risk_assessment'], (int, float, str)):
            # Convert simple score to full risk assessment object
            try:
                score = float(scan_data['risk_assessment'])
                scan_data['risk_assessment'] = {
                    'overall_score': score,
                    'risk_level': get_risk_level(score),
                    'color': get_color_for_score(score)
                }
            except:
                # Keep as is if we can't convert
                pass
        elif isinstance(scan_data['risk_assessment'], dict):
            # Ensure color exists
            if 'color' not in scan_data['risk_assessment'] and 'overall_score' in scan_data['risk_assessment']:
                score = scan_data['risk_assessment']['overall_score']
                scan_data['risk_assessment']['color'] = get_color_for_score(score)
    
    # Format risk levels for client-friendly display (from CybrScann-main)
    if 'risk_assessment' in scan_data:
        risk_level = scan_data['risk_assessment'].get('risk_level', 'Unknown')
        if risk_level.lower() == 'critical':
            scan_data['risk_color'] = 'danger'
        elif risk_level.lower() == 'high':
            scan_data['risk_color'] = 'warning'
        elif risk_level.lower() == 'medium':
            scan_data['risk_color'] = 'info'
        else:
            scan_data['risk_color'] = 'success'
    
    # Format dates for display (from CybrScann-main)
    if 'timestamp' in scan_data:
        try:
            dt = datetime.fromisoformat(scan_data['timestamp'])
            scan_data['formatted_date'] = dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            pass
    
    # Add summary statistics (from CybrScann-main)
    if 'risk_assessment' in scan_data:
        risk_assessment = scan_data['risk_assessment']
        scan_data['total_issues'] = (
            risk_assessment.get('critical_issues', 0) +
            risk_assessment.get('high_issues', 0) +
            risk_assessment.get('medium_issues', 0) +
            risk_assessment.get('low_issues', 0)
        )
    
    return scan_data

def detect_os_and_browser(user_agent):
    '''Detect OS and browser from user agent string'''
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
    
    return os_info, browser_info

def get_risk_level(score):
    '''Get risk level text based on score'''
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
    """Get appropriate color based on score"""
    if score >= 90:
        return '#28a745'  # green
    elif score >= 80:
        return '#5cb85c'  # light green
    elif score >= 70:
        return '#17a2b8'  # info blue
    elif score >= 60:
        return '#ffc107'  # warning yellow
    elif score >= 50:
        return '#fd7e14'  # orange
    else:
        return '#dc3545'  # red

def format_scan_results_for_client(scan_data):
    """Format scan results for client-friendly display"""
    try:
        if not scan_data:
            return None
        
        # Add client-friendly formatting
        formatted_scan = scan_data.copy()
        
        # Format risk levels
        if 'risk_assessment' in formatted_scan:
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
        if 'timestamp' in formatted_scan:
            try:
                dt = datetime.fromisoformat(formatted_scan['timestamp'])
                formatted_scan['formatted_date'] = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                pass
        
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
        return scan_data