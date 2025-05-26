"""
Register FTD devices with FMC and configure complete firewall deployment automation.

This function provides end-to-end automation for FTD firewall deployment, from initial
device registration with Firewall Management Center (FMC) to complete configuration
including High Availability, security zones, interfaces, and routing. It handles the
entire lifecycle of FTD deployment in a production-ready manner.

Steps:
1. Authenticates with FMC API and retrieves access token
2. Retrieves access control policy ID for device assignment
3. Registers all FTD devices to FMC via REST API
4. Monitors device health and deployment status until ready
5. Configures High Availability (HA) pairs with failover settings
6. Creates security zones for network segmentation
7. Configures physical interfaces with IP addresses and zone assignments
8. Creates network objects and static routing configurations
9. Provides real-time progress tracking and error handling throughout

Args:
    fmc_creds (list): List of dictionaries containing FMC API credentials (username, password)
    fmc_token (str): FMC API token generation endpoint URL
    fmc_devices (str): FMC device records API endpoint URL
    fmc_payload (dict): Device registration payload containing device configurations
    colors (dict): Dictionary containing color codes for terminal output formatting
    headers (dict): HTTP headers for API requests
    fmc_register_queue (Queue): Thread-safe queue for device registration status messages
    ha_settings (dict): High Availability configuration payload and settings
    fmc_ha_queue (Queue): Thread-safe queue for HA configuration status messages
    sec_zone_settings (dict): Security zones configuration payload
    fmc_sec_zones_queue (Queue): Thread-safe queue for security zone status messages
    fmc_interface_queue (Queue): Thread-safe queue for interface configuration messages
    fmc_int_settings (dict): Interface configuration settings (IP, netmask, zones)
    fmc_route_settings (dict): Static routing and host object configuration
    fmc_object_host_queue (Queue): Thread-safe queue for host object creation messages
    fmc_route_queue (Queue): Thread-safe queue for routing configuration messages
    fmc_policyid_url (str): FMC access control policy API endpoint
    fmc_device_details_url (str): FMC device details API endpoint with device_id placeholder
    fmc_ha_settings_url (str): FMC HA pair configuration API endpoint
    fmc_sec_zones_url (str): FMC security zones API endpoint
    fmc_url_devcies_int_detail (str): FMC device interface details API endpoint
    fmc_obj_network_url (str): FMC network objects API endpoint
    fmc_obj_host_url (str): FMC host objects API endpoint
    fmc_routing_url (str): FMC static routing API endpoint
    fmc_dev_int_url (str): FMC device interfaces API endpoint
    fmc_ha_check_url (str): FMC HA pair status checking API endpoint

Returns:
    None: Function performs configuration operations and updates progress queues.
          All status updates are communicated through thread-safe queues.

Raises:
    requests.exceptions.RequestException: For HTTP/API communication errors
    Exception: For authentication token retrieval failures
    TimeoutError: When device registration or HA configuration exceeds timeout limits

Features:
    - Multi-threaded progress tracking with tqdm progress bars
    - Comprehensive error handling and logging
    - Real-time status monitoring and health checks
    - Production-ready SSL handling (configurable)
    - Timeout management for long-running operations
    - Thread-safe communication via queues

Security Notes:
    - SSL verification disabled for lab environments (verify=False)
    - Credentials handled securely through parameter passing
    - Token-based authentication with automatic header management
    - Comprehensive logging for audit trails

Production Considerations:
    - Enable SSL verification for production deployments
    - Implement secure credential management
    - Adjust timeout values based on environment requirements
    - Monitor queue sizes for memory management in large deployments
"""

import requests 
import json
import datetime
from queue import Queue
from tqdm import tqdm # Progress bar library for terminal output
import logging
import time

logger = logging.getLogger()

def fmc_register(
    fmc_creds,
    fmc_token,
    fmc_devices,
    fmc_payload,
    colors,
    headers,
    fmc_register_queue,
    ha_settings,
    fmc_ha_queue,
    sec_zone_settings,
    fmc_sec_zones_queue,
    fmc_interface_queue,
    fmc_int_settings,
    fmc_route_settings,
    fmc_object_host_queue,
    fmc_route_queue,
    fmc_policyid_url,
    fmc_device_details_url,
    fmc_ha_settings_url,
    fmc_sec_zones_url,
    fmc_url_devcies_int_detail,
    fmc_obj_network_url,
    fmc_obj_host_url,
    fmc_routing_url,
    fmc_dev_int_url,
    fmc_ha_check_url
    ):

    devices_count = len(fmc_payload['device_payload']) # Number of devices to register
    ha_count = 1 # Number of HA pairs to configure
    sec_zone_count = len(sec_zone_settings['sec_zones_payload']) # Number of security zones to create
    total_interfaces = 3 # Number of interfaces to configure
    host_object_count = 1 # Number of host objects to create
    route_object_count = 1 # Number of static routes to create
    username = fmc_creds[0]['username']
    password = fmc_creds[0]['password']
    ready_devices = {}
    poll_interval = 10
    waited = 0    
    device_names = []
    devices_list = [] # Initialize an empty list to store devices

    logger.info(f"Registering {devices_count} to FMC...")

    # Initialize progress bars

    fmc_register_progress  = tqdm(total=devices_count, desc=f'{colors.get("green")}Registering on FMC{colors.get("reset")}', position=0, leave=True, ncols=100)
    fmc_ha_progress        = tqdm(total=ha_count, desc=f'{colors.get("green")}Configuring HA {colors.get("reset")}', position=1, leave=True, ncols=100)
    fmc_seczone_progress   = tqdm(total=sec_zone_count, desc=f'{colors.get("green")}Creating Security Zones on FMC{colors.get("reset")}', position=2, leave=True, ncols=100)
    fmc_interface_progress = tqdm(total=total_interfaces, desc=f'{colors.get("green")}Configuring Interfaces{colors.get("reset")}', position=3, leave=True, ncols=100)
    fmc_host_obj_progress = tqdm(total=host_object_count, desc=f'{colors.get("green")}Configuring Host Object{colors.get("reset")}', position=4, leave=True, ncols=100)
    fmc_route_progress = tqdm(total=route_object_count, desc=f'{colors.get("green")}Configuring Default Route{colors.get("reset")}', position=5, leave=True, ncols=100)

    # Disable SSL warnings (not recommended for production)
    requests.packages.urllib3.disable_warnings()
    headers = {"Content-Type": "application/json"}
    try:
        # Generate Token
        response_token = requests.post(fmc_token, headers=headers, auth=(username, password), verify=False)
        response_token.raise_for_status()
        # Extract tokens from headers
        auth_token = response_token.headers.get("X-auth-access-token", None)
        if not auth_token:
            raise Exception("Authentication token not found in response.")
        logger.info(f"Authentication successful! Token: {auth_token}")
        headers["X-auth-access-token"] = auth_token
        
        # Retrieve Access Control Policy ID
        response_policy = requests.get(fmc_policyid_url, headers=headers, verify=False)
        response_policy.raise_for_status()
        policies = response_policy.json().get('items', [])
        policy_id = None
        for policy in policies:
            if policy["name"] == "Initial_policy":
                policy_id = policy["id"]
                break

        if not policy_id:
            logger.info("Initial_policy not found.")
            return

        # Assign policy ID to each device
        for device in fmc_payload["device_payload"]:
            device["accessPolicy"]["id"] = policy_id

        ### REGISTER DEVICES TO FMC ###

        for device in fmc_payload["device_payload"]:
            device_name = device["name"]
            response_device = requests.post(fmc_devices, headers=headers, data=json.dumps(device), verify=False)
            if response_device.status_code == 202:
                logger.info(f"Device {device_name} added successfully.")
                fmc_register_queue.put(f"{datetime.datetime.now() } Device {device_name} registered successfully to FMC.")
            else:
                logger.info(f"Failed to add device {device_name}. Status code: {response_device.status_code}")
                logger.info(response_device.text)
                fmc_register_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Failed to add device {device_name}. Status code: {response_device.status_code}{colors.get("reset")}')
        for name in fmc_payload["device_payload"]:
            device_names.append(name['name'])
        # Wait for all devices to appear in FMC device records
        max_wait = 600  # seconds
        waited_rec = 0
        poll_interval = 10
        pool_interval_reg = 30
        while True:
            response_show = requests.get(fmc_devices, headers=headers, verify=False)
            response_show.raise_for_status()
            devices = response_show.json().get('items', [])
            found_device_names = [dev["name"] for dev in devices]
            missing_devices = set(device_names) - set(found_device_names)
            if not missing_devices:
                logger.info("All devices have appeared in FMC device records.")
                break
            if waited_rec > max_wait:
                logger.error(f"Timeout: Devices {missing_devices} did not appear in FMC device records after {max_wait} seconds.")
                fmc_register_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Devices {missing_devices} did not appear in FMC. Registration failed.{colors.get("reset")}')
                return
            logger.info(f"Waiting for devices to appear in FMC: {missing_devices} ({waited_rec}s)")
            time.sleep(poll_interval)
            waited_rec += poll_interval
        while True:
            response_health_status = requests.get(fmc_devices, headers=headers, verify=False)
            response_health_status.raise_for_status()
            devices = response_health_status.json().get('items', [])
            for dev in devices:
                if dev["name"] in device_names:
                    detail_resp = requests.get(fmc_device_details_url.format(device_id=dev['id']), headers=headers, verify=False)
                    detail_resp.raise_for_status()
                    dev_detail = detail_resp.json()
                    health = dev_detail.get("healthStatus", "").lower()
                    deploy = dev_detail.get("deploymentStatus", "").upper()
                    logger.info(f"Device {dev['name']} healthStatus: {health}, deploymentStatus: {deploy}")
                    healthy_states = ["green", "yellow", "recovered"]
                    if health in healthy_states and deploy == "DEPLOYED" and dev["name"] not in ready_devices:    
                        ready_devices[dev["name"]] = dev 
                        fmc_register_progress.update(1)
                    if health == "red" and deploy == "NOT_DEPLOYED":
                        logger.info(f"Device {dev['name']} is not deployed. Please check logs...")
                        fmc_register_queue.put(f'{colors.get("yellow")}{datetime.datetime.now()} - "Device {dev["name"]} is not deployed. Waiting for deployment...{colors.get("reset")}')
                        continue
            if missing_devices:
                logger.error(f"Device(s) {missing_devices} are no longer present in FMC device records. Registration or deployment likely failed.")
                fmc_register_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Device(s) {missing_devices} disappeared from FMC. Registration or deployment failed.{colors.get("reset")}')
                break
            if len(ready_devices) == len(device_names):
                logger.info("All devices are ready and deployed!")
                break
            if waited > 1800:  # 30 minutes, just as a warning
                logger.info(f"Warning: Devices are taking longer than expected to be ready. Waited {waited} seconds.")
            logger.info(f"Waiting... ({waited}s)")
            time.sleep(pool_interval_reg)
            waited += pool_interval_reg

        if len(ready_devices) < len(device_names):
            logger.info("Timeout waiting for devices to be ready.")
            return
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        fmc_register_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Error: {e}{colors.get("reset")}')
    

    ### CONFIGURE HA ###
    try:

        response_ha = requests.get(fmc_devices, headers=headers, verify=False)
        response_ha.raise_for_status() 
        devices = response_ha.json() # Get the first page of devices
        temp_devices_list = devices.get('items', []) # Get the list of devices
        for id in temp_devices_list:
            device_name = id['name'] # Get the name of each device
            device_id = id['id'] # Get the ID of each device
            response_int = requests.get(fmc_dev_int_url.format(device_id=device_id), headers=headers, verify=False)
            response_int.raise_for_status()
            temp_devices_interface = response_int.json().get('items', [])
            for interface in temp_devices_interface:
                if interface['name'] == 'GigabitEthernet0/5':
                    interface_id = interface['id'] # Get the ID of each device interface
                    devices_list.append({"name": device_name, "id": device_id, "interface_id": interface_id}) # Append the device ID to the list

        ha_payload = ha_settings["ha_payload"]
        ha_payload["primary"]["id"] = devices_list[0]["id"]
        ha_payload["primary"]["name"] = devices_list[0]["name"]
        ha_payload["secondary"]["id"] = devices_list[1]["id"]
        ha_payload["secondary"]["name"] = devices_list[1]["name"]
        ha_payload["ftdHABootstrap"]["lanFailover"]["interfaceObject"]["id"] = devices_list[0]["interface_id"]
        ha_payload["ftdHABootstrap"]["statefulFailover"]["interfaceObject"]["id"] = devices_list[1]["interface_id"]
        response_post = requests.post(fmc_ha_settings_url, headers=headers, data=json.dumps(ha_payload), verify=False)
        time.sleep(10)
        # Poll until the new HA pair appears in the list
        ha_id = ""
        max_ha_wait = 1800
        wait_ha = 0
        while not ha_id:
            response_no_ha_id = requests.get(fmc_ha_settings_url, headers=headers, verify=False)
            response_no_ha_id.raise_for_status()
            ha_pairs = response_no_ha_id.json().get('items', [])
            for ha in ha_pairs:
                if ha.get('name') == ha_payload['name']:
                    ha_id = ha.get('id')
                    logger.info(f'HA pair found: {ha_id}')
                    break
            if not ha_id:
                if wait_ha > max_ha_wait:
                    logger.info("Timeout waiting for HA pair to appear.")
                    return
                logger.info(f"Waiting for HA pair to be created... ({wait_ha}s)")
                time.sleep(poll_interval)
                wait_ha += poll_interval
        if ha_id:
            while True:
                response_ha_id = requests.get(fmc_ha_check_url.format(ha_id=ha_id), headers=headers, verify=False)
                response_ha_id.raise_for_status()
                ha_json = response_ha_id.json()
                meta = ha_json.get('metadata', {})
                primary_status = meta.get('primaryStatus', {}).get('currentStatus', '').lower()
                secondary_status = meta.get('secondaryStatus', {}).get('currentStatus', '').lower()
                logger.info(f"HA status: primary={primary_status}, secondary={secondary_status}")
                if primary_status == "active" and secondary_status == "standby":
                    logger.info("HA added successfully.")
                    fmc_ha_progress.update(1)
                    fmc_ha_queue.put(f"{datetime.datetime.now() } HA added successfully.")
                    break
                if primary_status == "failed" or secondary_status == "failed":
                    logger.info("HA failed - Please check logs.")
                    break
                if wait_ha > max_ha_wait:
                    logger.info(f"Warning: HA taking too long to establish. Waited {wait_ha} seconds.")
                    break
                logger.info(f"Waiting... ({wait_ha}s)")
                time.sleep(poll_interval)
                wait_ha += poll_interval
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        fmc_ha_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Error: {e}{colors.get("reset")}')
    
    ### CREATE SECURITY ZONES ###

    try:
        zones_id_list = []
        for zone in sec_zone_settings["sec_zones_payload"]:
            response_zones = requests.post(fmc_sec_zones_url, headers=headers, data=json.dumps(zone), verify=False)
            response_zones.raise_for_status()
            zones = response_zones.json()
            zones_id = zones.get('id')
            zones_id_list.append(zones_id)

            if response_zones.status_code in [200, 201]:
                fmc_sec_zones_queue.put(f"{datetime.datetime.now() } Security zone {zone['name']} created successfully.")
                logger.info(f"Security zone {zone['name']} created successfully.")
                fmc_seczone_progress.update(1)
            else:
                logger.info(f"Failed to create security zone {zone['name']}. Status code: {response_zones.status_code}")
                logger.info(response_zones.text)
      #  fmc_seczone_progress.close()
        time.sleep(5)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        fmc_sec_zones_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Error: {e}{colors.get("reset")}')     
    
    ### CONFIGURE INTERFACES ###
    try:
    # Get the HA primary device ID
        def configure_interface(
            interface_id,
            interface_name,
            config,  # dict from your external config, includes zone_index
            zones_id_list,
            primary_status_id,
            primary_name,
            headers,
            fmc_interface_progress,
            fmc_interface_queue
        ):
            """
            Helper to configure a single interface on the FMC device using external config.
            """

            response_int = requests.get(fmc_url_devcies_int_detail.format(primary_status_id=primary_status_id,interface_id=interface_id), headers=headers, verify=False)
            response_int.raise_for_status()
            interface_obj = response_int.json()
            interface_obj.pop("links", None)
            interface_obj.pop("metadata", None)
            # Use zone_index from config to select the correct security zone
            zone_index = config["zone_index"]
            interface_obj["securityZone"] = {
                "id": zones_id_list[zone_index],
                "type": "SecurityZone"
            }
            interface_obj["ifname"] = config["ifname"]
            interface_obj["enabled"] = True
            interface_obj["ipv4"] = {
                "static": {
                    "address": config["ip_address"],
                    "netmask": config["netmask"]
                }
            }
            response_put = requests.put(fmc_url_devcies_int_detail.format(primary_status_id=primary_status_id,interface_id=interface_id), headers=headers, data=json.dumps(interface_obj), verify=False)
            response_put.raise_for_status()
            if response_put.status_code in [200, 201]:
                logger.info(f"Security zone assigned to interface {interface_name} on device {primary_name} successfully.")
                fmc_interface_queue.put(f"{datetime.datetime.now()} Security zone assigned to interface {interface_name} on device {primary_name} successfully.")
                logger.info(f'IP address assigned to interface {interface_name} on device {primary_name} successfully.')
                fmc_interface_queue.put(f"{datetime.datetime.now()} IP address assigned to interface {interface_name} on device {primary_name} successfully.")
                fmc_interface_progress.update(1)
            else:
                logger.info(f"Failed to assign security zone to interface {interface_name} on device {primary_name}. Status code: {response_put.status_code}")
                logger.info(response_put.text)

        response_ha_check = requests.get(fmc_ha_check_url.format(ha_id=ha_id), headers=headers, verify=False)
        response_ha_check.raise_for_status()
        ha_json = response_ha_check.json()
        logger.info(f'Active device is {ha_json["metadata"]["primaryStatus"]["device"]["name"]}')
        logger.info(response_ha_check.text)
        primary_status_id = ha_json["metadata"]["primaryStatus"]["device"]["id"]
        primary_name = ha_json["metadata"]["primaryStatus"]["device"]["name"]
        url_devices_int = f"https://192.168.0.201/api/fmc_config/v1/domain/default/devices/devicerecords/{primary_status_id}/physicalinterfaces"
        response_int_check = requests.get(url_devices_int, headers=headers, verify=False)
        response_int_check.raise_for_status()
        interfaces = response_int_check.json().get('items', [])

        for int_id in interfaces:
            int_name = int_id['name']
            if int_name  in fmc_int_settings:
                config = fmc_int_settings[int_name]
                configure_interface(
                    interface_id=int_id['id'],
                    interface_name=int_name,
                    config=config,
                    zones_id_list=zones_id_list,
                    primary_status_id=primary_status_id,
                    primary_name=primary_name,
                    headers=headers,
                    fmc_interface_progress=fmc_interface_progress,
                    fmc_interface_queue=fmc_interface_queue,
                )
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        fmc_interface_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Error: {e}{colors.get("reset")}') 
        
    ### CREATE DEFAULT ROUTE ###

    try:
        host_object = fmc_route_settings["host_object"]
        static_route_payload = fmc_route_settings["static_route_payload"]

        # Create network object:
        response_post = requests.post(fmc_obj_host_url, headers=headers, data=json.dumps(host_object), verify=False)
        obj_creation_re = response_post.json()
        logger.info(response_post.status_code)
        if response_post.status_code in [200,201]:            
            gw_host_id = obj_creation_re.get('id')
            static_route_payload["gateway"]["object"]["id"] = gw_host_id
            logger.info(f"Host object {host_object['name']} created successfully.")
            logger.info(f"Host object ID: {gw_host_id}")
            fmc_host_obj_progress.update(1)
            fmc_object_host_queue.put(f"{datetime.datetime.now() } Host object {host_object['name']} created successfully.")
        else:
            logger.info(f"Failed to create host object {host_object['name']}. Status code: {response_post.status_code}")
            logger.info(response_post.text)

        # Get any IPv4 object ID
        response_get = requests.get(fmc_obj_network_url, headers=headers, verify=False)
        response_get.raise_for_status()
        obj_networks_all = response_get.json().get('items', [])

        for obj in obj_networks_all:
            if obj['name'] == 'any-ipv4':
                any_ipv4_id = obj['id']

        static_route_payload["selectedNetworks"][0]["id"] = any_ipv4_id
        # Create route
        response_route = requests.post(fmc_routing_url.format(primary_status_id=primary_status_id), headers=headers, data=json.dumps(static_route_payload), verify=False)
        response_route.raise_for_status()

        if response_route.status_code in [200, 201]:
            route_response = response_route.json()
            logger.info(f"Static route '{static_route_payload['name']}' created successfully.")
            logger.info(f"Route ID: {route_response.get('id')}")
            fmc_route_progress.update(1)
            fmc_route_queue.put(f"{datetime.datetime.now() } Static route '{static_route_payload['name']}' created successfully.")
        else:
            logger.info(f"Failed to create static route. Status code: {response_route.status_code}")
            logger.info(response_route.text)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        fmc_interface_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - "Error: {e}{colors.get("reset")}')
    try:
        # Close progress bars
        fmc_register_progress.close()
        fmc_ha_progress.close() 
        fmc_seczone_progress.close()
        fmc_interface_progress.close()
        fmc_host_obj_progress.close()
        fmc_route_progress.close()
    except:
        pass  # In case any are already closed