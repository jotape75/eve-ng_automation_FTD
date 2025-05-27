"""
Overview:
---------
The script authenticates with FMC using basic authentication, retrieves an access token, and performs API calls 
to gather information about devices, High Availability pairs, interfaces, security zones, routing, and network objects.
This is primarily used for testing API connectivity and exploring FMC REST API capabilities.

Functions:
----------
1. fmc_conn_test():
    - Authenticates with FMC API using username/password credentials
    - Generates and manages X-auth-access-token for subsequent API calls
    - Demonstrates various FMC REST API endpoints for device management
    - Performs GET requests to retrieve configuration data
    - Handles SSL verification bypass for lab environments
    - Pretty-prints JSON responses for analysis

API Endpoints Demonstrated:
---------------------------
- Token Generation: /api/fmc_platform/v1/auth/generatetoken
- Device Management: /api/fmc_config/v1/domain/default/devices/devicerecords
- High Availability: /api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs
- Interface Configuration: /physicalinterfaces
- Security Zones: /api/fmc_config/v1/domain/default/object/securityzones
- Static Routing: /routing/ipv4staticroutes
- Virtual Routers: /routing/virtualrouters
- Network Objects: /api/fmc_config/v1/domain/default/object/networks
- Deployment History: /api/fmc_config/v1/domain/default/deployment/jobhistories

Dependencies:
-------------
- requests: For HTTP/HTTPS API communication
- json: For JSON data parsing and formatting
- urllib3: For SSL warning suppression (disabled for lab environments)

Configuration:
--------------
Update the following variables for your environment:
- username: FMC API user account
- password: FMC API user password  
- url_token: FMC management IP address and token endpoint
- device_id: Target device UUID for device-specific operations
- ha_id: High Availability pair UUID
- interface_id: Physical interface UUID
- statiroute_id: Static route configuration UUID

Usage:
------
Run the script directly to test FMC API connectivity and retrieve configuration data:
    python fmc_api_gather_info.py

Security Notes:
---------------
- SSL verification is disabled (verify=False) for lab environments
- Credentials are hardcoded for testing purposes - use environment variables in production
- urllib3 warnings are suppressed for cleaner output in lab scenarios

Note:
-----
This script is designed for lab environments and API testing. For production use:
- Enable SSL verification
- Use secure credential management
- Implement proper logging
- Add comprehensive error handling and retry logic
"""

import requests
import json

def fmc_conn_test():
    username = 'api_user'
    password = 'Cisco1234!'

    requests.packages.urllib3.disable_warnings()
    url_token = "https://192.168.0.201/api/fmc_platform/v1/auth/generatetoken"
    headers = {"Content-Type": "application/json"}

    try:
        # Generate Token
        response = requests.post(url_token, headers=headers, auth=(username, password), verify=False)
        response.raise_for_status()
        auth_token = response.headers.get("X-auth-access-token", None)
        if not auth_token:
            raise Exception("Authentication token not found in response.")
        print(f"Authentication successful! Token: {auth_token}")
        headers["X-auth-access-token"] = auth_token

        device_id = "5f731edc-37b3-11f0-9f97-f415e9865023"
        ha_id = "f05c0e98-370b-11f0-af92-56a023ce6456"
        interface_id = "00000000-0000-0ed3-0000-017179912724"
        statiroute_id = "00000000-0000-0ed3-0000-017179920996"
        add_device_url = "https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords"
        dev_detail_url = f"https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}"
        ha_settings_url = f'https://192.168.0.201/api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs' 
        url_devices_int = f"https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}/physicalinterfaces"
        url_devices_int_id = f"https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}/physicalinterfaces/{interface_id}"
        ha_check_url = f'https://192.168.0.201/api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs/{ha_id}'
        deployments = f'https://192.168.0.201/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/deployment/jobhistories?expanded=true'
        sec_zones = f'https://192.168.0.201/api/fmc_config/v1/domain/default/object/securityzones'
        routing = f'https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}/routing/staticroutes'
        routing_id = f'https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}/routing/ipv4staticroutes/{statiroute_id}'
        object_network = f'https://192.168.0.201/api/fmc_config/v1/domain/default/object/networks'

        response = requests.get(add_device_url, headers=headers, verify=False)
        response.raise_for_status() 
        devices = response.json() # Get the first page of devices
        #print (response.status_code) # Print the status code
        #print(response.text)
        print(json.dumps(devices, indent=4)) # Print the devices
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
 

if __name__ == "__main__": 


    fmc_conn_test()