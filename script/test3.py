#!/usr/bin/env python3
import urllib3
import requests

# Disable warnings for self-signed certificates used in lab environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration Variables
SWITCH_IP = "192.168.250.12"
API_VERSION = "v10.18"
BASE_URL = f"https://{SWITCH_IP}/rest/{API_VERSION}/"

credentials = {
    "username": "admin",
    "password": "pass01"
}

# 1. Initialize the Persistent Request Session Object
session = requests.Session()

try:
    # 2. Authenticate to the Switch
    # Note: On firmware v10.09+, a CSRF token may also be generated in headers.
    login_url = f"{BASE_URL}login"
    login_response = session.post(login_url, data=credentials, verify=False, timeout=5)
    
    if login_response.status_code == 200:
        print(" Successfully authenticated to AOS-CX.")
        
        # 3. GET Request: Read Configured System VLANs
        vlan_url = f"{BASE_URL}system/vlans"
        get_response = session.get(vlan_url, verify=False, timeout=5)
        
        if get_response.status_code == 200:
            print("Current VLAN List JSON:", get_response.json())
            
        # 4. POST Request: Build a New VLAN Resource (VLAN 200)
        vlan_payload = {
            "id": 200,
            "name": "Automation_VLAN"
        }
        # Payload maps to the JSON model structure schema defined in Swagger documentation
        post_response = session.post(vlan_url, json=vlan_payload, verify=False, timeout=5)
        
        if post_response.status_code == 201:
            print(" Successfully generated VLAN 200.")
        else:
            print(f"Failed to build VLAN. Status: {post_response.status_code}, Context: {post_response.text}")
            
    else:
        print(f"Authentication failed. Status Code: {login_response.status_code}")

except requests.exceptions.RequestException as error:
    print(f"An explicit connection error occurred: {error}")

finally:
    # 5. Terminate and De-authenticate Session Profile safely
    logout_url = f"{BASE_URL}logout"
    logout_response = session.post(logout_url, verify=False, timeout=5)
    if logout_response.status_code == 200:
        print(" Session ended cleanly.")
    session.close()