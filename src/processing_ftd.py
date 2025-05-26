import requests 
import datetime 
import uuid # Unique identifier library
from telnetlib import Telnet # Python < 3.13
#from telnetlib3 import Telnet  # Python >= 3.13
import time
import datetime
import pandas as pd
import threading
from queue import Queue
from tqdm import tqdm
import logging
from vncdotool import api # VNC connection library
from PIL import Image, ImageEnhance, ImageFilter # Image processing library
import pytesseract # OCR library
import os
import json

logger = logging.getLogger()

# This function will be called to authenticate with the EVE-NG API
def user_auth(eve_API_creds,eve_ng_url_login,eve_authorization_header,colors):
    """
    Authenticate with the EVE-NG API using the provided credentials.

    This function sends a login request to the EVE-NG API using the supplied credentials
    and authorization header. It handles the authentication process, prints and logs
    the result, and returns the response and headers for further API calls.

    Steps:
    1. Extracts the username and password from the credentials list.
    2. Constructs the login payload and headers.
    3. Sends a POST request to the EVE-NG login endpoint.
    4. Checks the response for successful authentication.
    5. Prints and logs the result, and exits on failure.

    Args:
        eve_API_creds (list): List of dictionaries containing EVE-NG API credentials.
        eve_ng_url_login (str): URL for EVE-NG login.
        eve_authorization_header (str): Authorization header for EVE-NG API.
        colors (dict): Dictionary containing color codes for terminal output.

    Returns:
        tuple: A tuple containing the response object and headers for further API calls.
    """
    # Extract username and password from the credentials

    username = eve_API_creds[0]['username']
    password = eve_API_creds[0]['password']

    headers = {
        'Authorization': eve_authorization_header,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Define the payload with the username and password
    login_payload = {
        'username': username,
        'password': password,
        'html5': '-1'
    }
    response = requests.post(eve_ng_url_login, json=login_payload, headers=headers)

    if response.status_code == 200:
        print(f'\n{colors.get("blue")}logger to EVE-ng API - {eve_ng_url_login}{colors.get("reset")}')
        print(f'{datetime.datetime.now()} - Login successful\n')
        logger.info('logger to EVE-ng API - {eve_ng_url_login}')
    else:
        print(f'\n{datetime.datetime.now()} - Login failed')
        print(response.text)
        logger.info(f'\n{datetime.datetime.now()} - Login failed')
        exit()
    return response,headers

# This function will be called to create nodes in EVE-NG
def create_network_HA(response,networks_url):

    """
    Create a High Availability (HA) network in the EVE-NG lab.

    This function sends a POST request to the EVE-NG API to create a new bridge network
    specifically for High Availability (HA) connections between devices. It uses the provided
    authenticated session (response) to authorize the request.

    Steps:
    1. Defines the network payload for a bridge named "ha_connection".
    2. Sends a POST request to the EVE-NG networks endpoint to create the network.
    3. Parses the response to retrieve the network ID.
    4. Logs the creation and returns the HA network ID.

    Args:
        response (requests.Response): Authenticated response object containing session cookies.

    Returns:
        str: The ID of the created HA network.
    """
        
    network_payload = {
    "type": "bridge",
    "name": "ha_connection",
    "left": 100,
    "top": 100,
    "visibility": 1
    }
    # Create network for HA connection
    net_response = requests.post(networks_url, json=network_payload, cookies=response.cookies)
    HA_network_id = net_response.json()["data"]["id"]
    logger.info(f"Network ID for HA connection created: {HA_network_id}.")

    return HA_network_id

def create_nodes(dev_num, node_type, device_payload, *args):
    (
    response,
    headers,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    createnode_queue,
    starnode_queue,
    connectnode_queue,
    configure_queue,
    closeconnection_queue,
    lock,
    colors,
    HA_network_id
    ) = args

    """
    Create and connect a node in EVE-NG using the provided payload and configuration.

    This function automates the creation of a network device node in EVE-NG, connects its management
    and HA interfaces to the appropriate networks, and reports progress and results via queues.

    Steps:
    1. Assigns a unique UUID to the device payload for identification.
    2. Optionally adjusts node placement for specific device numbers.
    3. Sends a POST request to the EVE-NG API to create the node.
    4. Retrieves the node's ID and interface details from the API.
    5. Connects the node's management and HA interfaces to the correct networks.
    6. Logs and queues status messages for each step.
    7. Retries node creation up to a maximum number of attempts if errors occur.

    Args:
        dev_num (int): Device number for the node instance.
        node_type (str): Type of the node (e.g., "FTD Firewall").
        device_payload (dict): Payload containing node configuration.
        *args: Additional arguments required for API calls and queue management.

    Returns:
        str: The ID of the created node if successful.

    Raises:
        Exception: If node creation fails after all retry attempts.
    """


    max_retries = 3  # Number of retries for node creation
    for attempt in range(max_retries):
        try:
            # Assign a unique UUID to the device payload
            logger.info(f"Attempting to create node {node_type} (Attempt {attempt + 1}/{max_retries}).")
            device_payload['uuid'] = str(uuid.uuid4())
            if dev_num == 1:
                device_payload['top'] = "30"  # Example adjustment for specific devices

            # Send the API request to create the node
            create_node_api = requests.post(eve_node_creation_url, json=device_payload, headers=headers, cookies=response.cookies)
            logger.debug(f"Create Node API Response: {create_node_api.text}")

            # Check if the node creation was successful
            if create_node_api.status_code != 201:
                raise ValueError(f"Failed to create node: {create_node_api.text}")

            # Parse the response to get the device ID
            create_node_response = create_node_api.json()
            device_id = create_node_response['data']['id']
            logger.info(f"Node {node_type} with ID {device_id} created successfully.")
            createnode_queue.put(f'{datetime.datetime.now()} - {node_type} - Eve-ng Node {device_id} created successfully')

            # Get device interface
            node_interface_api = requests.get(node_interface.format(device_id=device_id), headers=headers, cookies=response.cookies)
            node_interface_response = node_interface_api.json()
            node_interface_id = node_interface_response["data"]["ethernet"][0]["name"]  # index 0 is the eth0/mgmt
            node_interface_id_ha = node_interface_response["data"]["ethernet"][7]["name"] # index 7 is the G0/5 interface

            logger.info(f"Node {node_type} with ID {device_id} has interface {node_interface_id}.")

            # Get management network name
            mgmt_net_api = requests.get(network_mgmt, headers=headers, cookies=response.cookies)
            mgmt_net_response = mgmt_net_api.json()
            mgmt_net_id = mgmt_net_response['data']['name']
            logger.info(f"Management network ID for {node_type} with ID {device_id}: {mgmt_net_id}.")

            # Connect device to management network
            interfaces = '{"0":"21"}'  # Adjust the management network ID for your environment
            interface_connection_api = requests.put(eve_interface_connection.format(device_id=device_id), data=interfaces, headers=headers, cookies=response.cookies)
            logger.info(f"Connected {node_type} with ID {device_id} to management network.")
            createnode_queue.put(f'{datetime.datetime.now()} - Connecting MGMT interface {node_interface_id} of {node_type} Eve-ng id {device_id} to management network {mgmt_net_id}')



            # Connect interfaces for High Availability (HA)
            interfaces = json.dumps({"7": HA_network_id}) #7 is the index of the interface G0/5
            int_conn_response = requests.put(node_interface.format(device_id=device_id),data=interfaces,headers=headers,cookies=response.cookies)
            logger.info (f'{datetime.datetime.now()} - Connecting interface {node_interface_id_ha} of {node_type} Eve-ng id {device_id} to management network {HA_network_id}')
            createnode_queue.put(f'{datetime.datetime.now()} - Connecting interface {node_interface_id_ha} of {node_type} Eve-ng id {device_id} to management network {HA_network_id}')

            return device_id

        except Exception as e:
            # Log the error and retry if attempts remain
            logger.error(f"Attempt {attempt + 1} to create node failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                # If all retries fail, log and raise the error
                createnode_queue.put(f'{datetime.datetime.now()} - Node creation failed after {max_retries} attempts')
                logger.critical(f"Failed to create node {node_type} after {max_retries} attempts.")
                raise

    # This part should never be reached due to the raise statement above
    return None
# This function will be called to start nodes in EVE-NG
def start_nodes(device_id, node_type, *args):
    (
    response,
    headers,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    createnode_queue,
    starnode_queue,
    connectnode_queue,
    configure_queue,
    closeconnection_queue,
    lock,
    colors,
    HA_network_id
    ) = args

    """
    Start a node in EVE-NG and verify it is running.

    This function sends a request to the EVE-NG API to start a specified node (device),
    then polls the API to confirm the node has reached the "running" state. It logs and
    queues status messages for monitoring and error handling.

    Steps:
    1. Sends a GET request to the EVE-NG API to start the node.
    2. Waits briefly, then polls the node status up to a maximum number of retries.
    3. If the node is running, logs and queues a success message.
    4. If the node fails to start or does not reach the running state in time, logs and queues an error.

    Args:
        device_id (str): The ID of the node/device to start.
        node_type (str): The type of the node (e.g., "FTD Firewall").
        *args: Additional arguments required for API calls, progress bars, and queues.

    Returns:
        bool: True if the node started successfully and is running, False otherwise.
    """
    logger.info(f"Attempting to start node {node_type} with ID {device_id}.")
    starnode_queue.put(f'{datetime.datetime.now()} - Starting {node_type} Eve-ng node {device_id} ')

    # Send the API request to start the node
    start_node_api = requests.get(eve_start_nodes_url.format(device_id=device_id), headers=headers, cookies=response.cookies)
    time.sleep(3)  # Add a delay of 3 seconds

    if start_node_api.status_code == 200:
        logger.info(f"Node {node_type} with ID {device_id} started successfully.")
        starnode_queue.put(f'{datetime.datetime.now()} - Node {device_id} - {node_type} started successfully')

        # Poll the EVE-NG API to check if the node is running
        max_retries = 10  # Maximum number of retries
        retry_delay = 5  # Delay between retries in seconds
        for attempt in range(max_retries):
            node_status_api = requests.get(f"{eve_node_creation_url}/{device_id}", headers=headers, cookies=response.cookies)
            if node_status_api.status_code == 200:
                try:
                    node_status = node_status_api.json().get('data', {}).get('status', None)
                    logger.debug(f"Node {node_type} with ID {device_id} status: {node_status} (Attempt {attempt + 1}/{max_retries})")
                    
                    if node_status == 2:  # 2 indicates the node is running
                        logger.info(f"Node {node_type} with ID {device_id} is running.")
                        return True  # Exit the function as the node is ready
                    elif node_status == 0:  # 0 indicates the node is stopped
                        logger.warning(f"Node {node_type} with ID {device_id} is stopped. (Attempt {attempt + 1}/{max_retries})")
                        start_node_api = requests.get(eve_start_nodes_url.format(device_id=device_id), headers=headers, cookies=response.cookies)
                        if start_node_api.status_code == 200:
                            logger.info(f"Retry to start node {node_type} with ID {device_id} was successful.")
                        else:
                            logger.error(f"Retry to start node {node_type} with ID {device_id} failed. Response: {start_node_api.text}")
                    else:
                        logger.warning(f"Unexpected status for node {node_type} with ID {device_id}: {node_status}")
                except Exception as e:
                    logger.error(f"Error parsing node status for {node_type} with ID {device_id}: {e}")
            else:
                logger.error(f"Failed to retrieve status for node {node_type} with ID {device_id}. Response: {node_status_api.text}")
            time.sleep(retry_delay)  # Wait before checking again

        # If the node is not ready after retries
        logger.error(f"Node {node_type} with ID {device_id} failed to start in time.")
        starnode_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - Node {device_id} - {node_type} failed to start in time{colors.get("reset")}')
    else:
        logger.error(f"Failed to start node {node_type} with ID {device_id}. Response: {start_node_api.text}")
        starnode_queue.put(f'{colors.get("red")}{datetime.datetime.now()} - Failed to start Eve-ng {device_id} - {node_type}{colors.get("reset")}')

    return False

def get_node_port(device_id,*args):
    (
    response,
    headers,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    createnode_queue,
    starnode_queue,
    connectnode_queue,
    configure_queue,
    closeconnection_queue,
    lock,
    colors,
    HA_network_id
    ) = args

    """
    Retrieve the port information for a created node in EVE-NG.

    This function queries the EVE-NG API to obtain the console port and node name
    for a given device ID. The port is typically used for Telnet or VNC access to
    the node's console for further configuration.

    Steps:
    1. Sends a GET request to the EVE-NG API to retrieve port information for the node.
    2. Parses the response to extract the port number and node name.
    3. Returns the port and name for use in console connections.

    Args:
        device_id (str): The ID of the device to get port information for.
        *args: Additional arguments required for API calls (unpacked from the main thread).

    Returns:
        tuple: A tuple containing the port number (str) and the node name (str).
    """

    # Get node port information
    node_port_api = requests.get(eve_node_port.format(device_id=device_id), headers=headers, cookies=response.cookies)
    port = node_port_api.json()['data']['url'].split(':')[-1]
    name = node_port_api.json()['data']['name']
    return port, name

# This function will be called to configure the node using Telnet
# Eve-ng uses Telnet to connect to the nodes as a console connection

def telnet_conn(port, name, device_id, dev_num, node_type,ftd_config,ftd_pwd,ftd_screen_shot, *args):
    (
    response,
    headers,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    createnode_queue,
    starnode_queue,
    connectnode_queue,
    configure_queue,
    closeconnection_queue,
    lock,
    colors,
    HA_network_id
    ) = args

    """
    Connect to a node in EVE-NG using Telnet/VNC and apply the initial configuration.

    This function establishes a console connection to the specified node using Telnet or VNC,
    automates the initial setup process (including login, password, EULA acceptance, and basic config),
    and applies device-specific configuration commands. It uses OCR to read screen prompts and
    simulates keypresses for automation. Status and errors are logged and sent to queues.

    Steps:
    1. Establishes a Telnet or VNC connection to the node's console port.
    2. Waits for login and password prompts, then sends credentials.
    3. Accepts the EULA and sets the admin password.
    4. Handles IPv4/IPv6 configuration prompts.
    5. Reads and applies configuration commands from an Excel file.
    6. Completes initial setup (e.g., manager registration, firewall mode).
    7. Logs progress and errors, and closes the connection when done.

    Args:
        port (str): The port number for the Telnet/VNC connection.
        name (str): The name of the node.
        device_id (str): The ID of the device.
        dev_num (int): The device number.
        node_type (str): Type of the node (e.g., "FTD Firewall").
        ftd_config (str): Path to the Excel file with configuration commands.
        ftd_pwd (str): Path to the file containing the admin password.
        *args: Additional arguments for API calls, queues, and configuration.

    Returns:
        None
    """
    # Define the screen file paths
    screen_file_path = os.path.join(
    ftd_screen_shot,
    f"screen_{node_type}_{device_id}.png"
    )
    # Define the processed screen file path for OCR better resolution
    screen_file_path_processed = os.path.join(
    ftd_screen_shot,
    f"_processed_screen_{node_type}_{device_id}.png"
    )

    # Telnet connection
    # Define the Telnet connection parameters
    TELNET_TIMEOUT = 10
    HOST = '192.168.0.119'
    tn = None  # Initialize tn to None to avoid issues for non-Telnet devices
    try:
        client = api.connect(f"{HOST}::{port}")
        connectnode_queue.put(f"{datetime.datetime.now()} - Connected to the {node_type} - node {device_id} on port {port}")
        logger.info(f"Connected to the {node_type} node {device_id} on port {port}")

        # Helper function to send text
        def send_text(text):
            for char in text:
                client.keyPress(char)  # Send each character individually
                time.sleep(0.2)  # Add a small delay between each keypress
            time.sleep(2)  # Add a delay after sending the full text

        # Helper function to capture and process screen text
        def capture_screen_text():

            with open(screen_file_path, "wb") as fp:
                client.captureScreen(fp)

            # Improved OCR preprocessing
            screen_image = Image.open(screen_file_path)
            screen_image = screen_image.convert("L")  # Convert to grayscale
            screen_image = screen_image.filter(ImageFilter.SHARPEN)  # Sharpen the image
            screen_image = ImageEnhance.Contrast(screen_image).enhance(2)  # Increase contrast
            screen_image = screen_image.resize((screen_image.width * 2, screen_image.height * 2))  # Resize for better OCR
            screen_image.save(screen_file_path_processed)  # Save for debugging
            extracted_text = pytesseract.image_to_string(screen_image, config="--psm 6")
    
            logger.info(f"OCR extracted {len(extracted_text)} characters")
            logger.info(f"OCR text: {repr(extracted_text)}")  # This shows exactly what OCR reads
    
            return extracted_text
        # Step 1: Wait for the login prompt
        connectnode_queue.put(f"{datetime.datetime.now()} - Waiting for {node_type} node {device_id} to start...")
        while True:
            screen_text = capture_screen_text()
            if "firepower login:" in screen_text.lower():
                send_text("admin")
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 2: Wait for the password prompt
        while True:
            screen_text = capture_screen_text()
            if "password" in screen_text.lower():
                send_text("Admin123")
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 3: Accept the EULA
        while True:
            screen_text = capture_screen_text() 
            if "press <enter> to display the eula:" in screen_text.lower():
                break
            time.sleep(5)
        client.keyPress("enter")
        time.sleep(2)
    # Waiting for the EULA agreement prompt
        while True:
            screen_text = capture_screen_text()
            if "yes" in screen_text.lower() and "agree to the eula" in screen_text.lower():
                send_text("YES")
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 4: Set the admin password
        configure_queue.put(f"{datetime.datetime.now()} - Applying initial configuration for {node_type} node {device_id}")
        logger.info(f"Applying initial configuration for {node_type} node {device_id}")
        while True:
            screen_text = capture_screen_text()
            if "enter new password:" in screen_text.lower():
                break
            time.sleep(5)
        with open(ftd_pwd, 'r') as pwd_file:
            new_password = pwd_file.read()
        send_text(new_password)
        client.keyPress("enter")
        time.sleep(2)
        send_text(new_password)
        client.keyPress("enter")
        time.sleep(2)
        while True:
            screen_text = capture_screen_text()
            if "password successfully changed" in screen_text.lower():
                break
            time.sleep(5)
        # Step 5: Handle IPv4 configuration prompt
        while True:
            screen_text = capture_screen_text()
            if "do you want to configure ipv4?" in screen_text.lower():
                client.keyPress("y")  # Respond 'y' to configure IPv4
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 6: Configure IPv4 (No OCR needed)
        client.keyPress("n")  # Skip IPv6 configuration
        client.keyPress("enter")
        time.sleep(1)
        commands_ftd = pd.read_excel(ftd_config, sheet_name=None)
        if str(dev_num) in commands_ftd:
        # Drop NaN values and convert the 'Command' column to a list
            commands = commands_ftd[str(dev_num)] ['Command'].dropna().tolist()
            for command in commands:
                send_text(command)  # Choose manual configuration
                client.keyPress("enter")
                time.sleep(1)
        time.sleep(5)  # Wait for the network configuration to apply
        # Step 7: Manage the device locally
        while True:
            screen_text = capture_screen_text()
            if "manage the device locally?" in screen_text.lower():
                send_text("no")  # Choose not to manage locally
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 8: Configure firewall mode
        while True:
            screen_text = capture_screen_text()
            if "configure firewall mode" in screen_text.lower():
                send_text("routed")  # Set firewall mode to routed
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 9: Configure firewall manager
        while True:
            screen_text = capture_screen_text()
            if ">" in screen_text.lower():
                send_text("configure manager add 192.168.0.201 cisco123")  # Set firewall mode to routed
                client.keyPress("enter")
                time.sleep(2)
                break
            time.sleep(5)
        # Step 9: Complete the setup / Disconnect from the VNC session
        try:
            if client:
                client.disconnect()
        except Exception as e:
            configure_queue.put(f"{datetime.datetime.now()} - An error occurred while disconnecting from {node_type} node {device_id}: {e}")
            logger.error(f"An error occurred while disconnecting from {node_type} node {device_id}: {e}")
        finally:
            if node_type == "FTD Firewall":
                closeconnection_queue.put(f"{datetime.datetime.now()} - Configuration complete - Closed the connection for {node_type} node {device_id}")
                logger.info(f"Configuration complete - Closed the connection for {node_type} node {device_id}")
                os.remove(screen_file_path)
                os.remove(screen_file_path_processed)
    except Exception as e:
        print(f"{datetime.datetime.now()} - An error occurred while configuring {node_type} node {device_id}: {e}")
        logger.info(f"An error occurred while configuring {node_type} node {device_id}: {e}")
        configure_queue.put(f"{datetime.datetime.now()} - An error occurred while configuring {node_type} node {device_id}: {e}")
    finally:
        # Close Telnet connection if it was initialized
        if tn:
            try:
                tn.close()
                closeconnection_queue.put(f"{datetime.datetime.now()} - Telnet connection closed for {node_type} node {device_id}")
                logger.info(f"Telnet connection closed for {node_type} node {device_id}")
            except Exception as close_error:
                connectnode_queue.put(f"{datetime.datetime.now()} - Error while closing Telnet connection: {close_error}")
                logger.error(f"Error while closing Telnet connection: {close_error}")


# Trheading function to create and manage nodes
# This function will create threads for each node type and manage their execution
# It will also handle the termination event to ensure graceful shutdown

def run_threads(
    nodes,
    response,
    threading_process,
    headers, 
    ftd_payload, 
    ftd_config, 
    ftd_pwd,
    ftd_screen_shot,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    colors,
    HA_network_id 
):
    """
    Create and manage threads for node creation, startup, and configuration in EVE-NG.

    This function orchestrates the parallel deployment and configuration of multiple network
    device nodes (such as Cisco FTD firewalls) in EVE-NG using Python threading. It initializes
    progress bars and message queues for each stage, starts threads for each device, and ensures
    all threads complete before returning results.

    Steps:
    1. Initializes queues and progress bars for thread-safe communication and status tracking.
    2. Iterates over the list of nodes and creates a thread for each device instance.
    3. Starts all threads and waits for their completion.
    4. Closes all progress bars after threads finish.
    5. Returns all message queues for further processing or result collection.

    Args:
        nodes (list): List of dictionaries specifying node types and their counts.
        response (requests.Response): Authenticated response object from the EVE-NG API.
        threading_process (function): Function to be executed by each thread for node lifecycle.
        headers (dict): HTTP headers for API requests.
        ftd_payload (dict): Payload for FTD firewall nodes.
        ftd_config (str): Path to the Excel file with configuration commands.
        ftd_pwd (str): Path to the file containing the admin password.
        eve_node_creation_url (str): URL for node creation API.
        eve_start_nodes_url (str): URL for starting nodes API.
        eve_node_port (str): URL for retrieving node port information.
        eve_interface_connection (str): URL for connecting node interfaces.
        node_interface (str): URL for retrieving node interface information.
        network_mgmt (str): URL for management network API.
        colors (dict): Dictionary containing color codes for terminal output.
        HA_network_id (str): Network ID for High Availability setup.

    Returns:
        tuple: A tuple containing all message queues for node creation, startup, connection,
               configuration, connection closure, and FMC registration/status.
    """
    # Initialize queues and locks for thread-safe communication
    threads = []
    createnode_queue = Queue()
    starnode_queue = Queue()
    connectnode_queue = Queue()
    configure_queue = Queue()
    fmc_register_queue = Queue()
    fmc_ha_queue = Queue()
    fmc_sec_zones_queue = Queue()
    fmc_interface_queue = Queue()
    fmc_object_host_queue = Queue()
    fmc_route_queue = Queue()
    closeconnection_queue = Queue()
    lock = threading.Lock()

  
    print(f'\n{colors.get("green")}\u2615 \u2615 Please grab a coffee and relax... This may take up to 30 mins.. \u2615 \u2615 {colors.get("reset")}')
    print(f'{colors.get("green")}\U0001F4DD \U0001F4DD Please take a look at the log file for detailed progress information! \U0001F4DD \U0001F4DD{colors.get("reset")}\n')

    # Calculate the total number of devices
    total_devices = sum(value for dev in nodes for value in dev.values())
    print(f'\n{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}')
    print(f'{colors.get("blue")}Total devices to be created: {colors.get("reset")}{total_devices}')
    print(f'{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}\n')
    

    # Create a tuple of arguments to be passed to the threading_process function
    args_var = (
        response,
        headers,
        eve_node_creation_url,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        node_interface,
        network_mgmt,
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue,
        lock,
        colors,
        HA_network_id
    )

    # Create progress bars with consecutive positions
    create_progress = tqdm(total=total_devices, desc=f'{colors.get("blue")}Creating Nodes{colors.get("reset")}', position=0, leave=True, ncols=100)
    start_progress = tqdm(total=total_devices, desc=f'{colors.get("blue")}Starting Nodes{colors.get("reset")}', position=1, leave=True, ncols=100)
    connect_progress = tqdm(total=total_devices, desc=f'{colors.get("blue")}Connecting Nodes{colors.get("reset")}', position=2, leave=True, ncols=100)
    configure_progress = tqdm(total=total_devices, desc=f'{colors.get("blue")}Configuring Nodes{colors.get("reset")}', position=3, leave=True, ncols=100)
    close_progress = tqdm(total=total_devices, desc=f'{colors.get("blue")}Closing Connections{colors.get("reset")}', position=4, leave=True, ncols=100)

    # Create threads for all devices
    for dev in nodes:  # Loop through each dictionary in the nodes list
        for node_type, value in dev.items():  # Loop through each device type and count
            for dev_num in range(value):  # Create a thread for each instance
                if node_type == "FTD Firewall":
                    th = threading.Thread(
                        target=threading_process,
                        args=(dev_num, node_type, ftd_payload,ftd_config,ftd_pwd,ftd_screen_shot,create_progress, start_progress, connect_progress, configure_progress, close_progress, *args_var),
                    )
                    threads.append(th)
                    time.sleep(3)   # Default delay for others
                else:
                    print(f'{colors.get("red")}{datetime.datetime.now()} - Unsupported node type: {node_type}{colors.get("reset")}')

    # Start all threads
    for th in threads:
        th.start()

    # Wait for all threads to finish
    for th in threads:
        th.join()

    # Close progress bars
    create_progress.close()
    start_progress.close()
    connect_progress.close()
    configure_progress.close()
    close_progress.close()
    
    return (
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue
    ),fmc_register_queue,fmc_ha_queue,fmc_sec_zones_queue,fmc_interface_queue,fmc_object_host_queue,fmc_route_queue

    

     
# This function will be called by each thread to handle the node creation and management
# It will call the process_node function to handle the node creation, starting, and port retrieval

def threading_process(
    dev_num, 
    node_type, device_payload,
    ftd_config,
    ftd_pwd, 
    ftd_screen_shot,
    create_progress, 
    start_progress, 
    connect_progress, 
    configure_progress, 
    close_progress,
    *args
    ):
    """
    Process a single node by creating, starting, and configuring it in EVE-NG.

    This function is designed to be run in a separate thread for each device instance.
    It handles the full lifecycle of a node: creation, startup, port retrieval, and initial configuration.
    Progress bars and message queues are updated at each stage for monitoring and logging.

    Steps:
    1. Calls `create_nodes` to create the node in EVE-NG and updates the creation progress bar.
    2. Calls `start_nodes` to start the node and updates the start progress bar.
    3. Calls `get_node_port` to retrieve the console port and updates the connect progress bar.
    4. Calls `telnet_conn` to connect to the node and apply the initial configuration, updating the configure progress bar.
    5. Updates the close progress bar after configuration is complete.
    6. Handles and logs any exceptions, reporting errors to the appropriate queue.

    Args:
        dev_num (int): The device number for this node instance.
        node_type (str): The type of node (e.g., "FTD Firewall").
        device_payload (dict): The payload for node creation.
        ftd_config (str): Path to the Excel file with configuration commands.
        ftd_pwd (str): Path to the file containing the admin password.
        create_progress (tqdm): Progress bar for node creation.
        start_progress (tqdm): Progress bar for node startup.
        connect_progress (tqdm): Progress bar for node connection.
        configure_progress (tqdm): Progress bar for node configuration.
        close_progress (tqdm): Progress bar for closing connections.
        *args: Additional arguments required for API calls, queues, and configuration.

    Returns:
        None
    """
    # Unpack only the elements from args_var
    (
    response,
    headers,
    eve_node_creation_url,
    eve_start_nodes_url,
    eve_node_port,
    eve_interface_connection,
    node_interface,
    network_mgmt,
    createnode_queue,
    starnode_queue,
    connectnode_queue,
    configure_queue,
    closeconnection_queue,
    lock,
    colors,
    HA_network_id
    ) = args

    try:
        # Step 1: Create the node
        device_id = create_nodes(dev_num, node_type, device_payload, *args)
        create_progress.update(1)

        # Step 2: Start the node
        start_nodes(device_id, node_type, *args)
        start_progress.update(1)

        # Step 3: Get the node's port information
        port, name = get_node_port(device_id, *args)
        connect_progress.update(1)

        # Step 4: Configure the node
        telnet_conn(port, name, device_id, dev_num, node_type, ftd_config, ftd_pwd,ftd_screen_shot, *args)
        configure_progress.update(1)

        # Step 5: Register the node on FMC - Runnng outside the thread

        # Step 6: Close the connection
        close_progress.update(1)

    except Exception as e:
        closeconnection_queue.put(f'{colors.get("red")}Error processing node {node_type} instance {dev_num}: {e}{colors.get("reset")}')