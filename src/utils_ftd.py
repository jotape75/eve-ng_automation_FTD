import json
import pandas as pd # Data manipulation library
from exceptions_ftd import FileNotFoundError, InvalidConfigurationError, InvalidDataError
import pyfiglet # ASCII art library
import logging

logger = logging.getLogger()


def display_message(colors):
    """
    Display an ASCII art message with a border and additional information.
    Args:
        colors (dict): A dictionary containing color codes for formatting.
    Returns:
        str: The formatted message with ASCII art and additional information.
    """  
    # Generate smaller ASCII art using the "univers" font
    ascii_art = pyfiglet.figlet_format("! BoUnCeR *", font="standard")
    ascii_lines = ascii_art.splitlines()  # Split the ASCII art into lines

    # Determine the width of the square
    max_width = max(len(line) for line in ascii_lines)  # Find the widest line in the ASCII art
    square_width = max(max_width, 50)  # Ensure the square is at least 50 characters wide

    # Create the top border of the square
    message = f"{colors.get('blue')}" + "#" * (square_width + 4) + "\n"

    # Add empty padding lines
    message += f"# {''.ljust(square_width)} #\n" * 2

    # Add the ASCII art inside the square
    for line in ascii_lines:
        message += f"# {line.ljust(square_width)} #\n"

    # Add the additional message and center it
    additional_message = "Eve-ng Cisco FTD Firewall automated \n deployment using Python"
    for line in additional_message.split("\n"):
        message += f"# {line.center(square_width)} #\n"

    # Add more empty padding lines
    message += f"# {''.ljust(square_width)} #\n" * 2

    # Add the GitHub profile and center it
    github_line = "GitHub Profile:  https://github.com/jotape75"
    message += f"# {colors.get('green')}{github_line.center(square_width)}{colors.get('reset')}{colors.get('blue')} #\n"

    # Add more empty padding lines
    message += f"# {colors.get('blue')}{''.ljust(square_width)} #\n" * 2

    # Create the bottom border of the square
    message += "#" * (square_width + 4) + f"{colors.get('reset')}\n"

    return message

def color_text():
    """
    Define color codes for terminal output.

    Returns:
        dict: A dictionary containing color codes for formatting.   
    """

    # Define color codes for terminal output
    green = "\033[1;32m"
    red = "\033[1;31m"
    yellow = "\033[1;33m"
    blue = "\033[1;34m"
    reset = "\033[0m"
    colors = {
        "green": green,
        "red": red,
        "yellow": yellow,
        "blue": blue,
        "reset": reset
    }
    return colors

def file_path():

    """
    Load all configuration files, device payloads, and credentials for the automation workflow.

    This function reads the main JSON configuration file, Excel files for device and FMC credentials,
    and additional JSON payloads for FTD nodes, HA, and security zones. It validates the presence and
    structure of all required files and data, raising custom exceptions for missing or malformed content.

    Steps:
    1. Loads the main automation configuration JSON file to retrieve file paths and API URLs.
    2. Loads device credentials from an Excel file and validates required columns.
    3. Loads FTD node payloads, HA payloads, and security zone payloads from JSON files.
    4. Loads FMC device data from an Excel file and validates required columns.
    5. Extracts and structures all relevant data for use in the main automation workflow.

    Args:
        None

    Returns:
        tuple: A tuple containing all loaded and validated data, including:
            - Device credentials and payloads
            - FTD and FMC configuration file paths
            - API URLs and headers
            - HA and security zone settings
            - FMC device registration payloads

    Raises:
        FileNotFoundError: If any required configuration or data file is missing.
        InvalidConfigurationError: If a configuration file is malformed.
        InvalidDataError: If required data is missing or invalid in the Excel files.
    """

    try:
        # Open the configuration file
        with open('/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation_FTD/data/automation_urls_ftd.json', 'r') as config_file:
            files_path = json.load(config_file)
            #EVE-NG parameters
            database_file = files_path["urls"]['data_file']
            eve_ng_url_login = files_path["api_urls"]["eve_ng_url_login"]
            eve_node_creation_url = files_path['api_urls']['eve_node_creation_url']
            eve_authorization_header = files_path['eve_authorization_header']
            eve_start_nodes_url = files_path["api_urls"]["eve_start_node_url"]
            eve_node_port = files_path["api_urls"]["eve_node_port"]
            eve_interface_connection = files_path["api_urls"]["eve_interface_connection_url"]
            node_interface = files_path["api_urls"]["eve_node_interface_url"]
            network_mgmt = files_path["api_urls"]["eve_network_mgmt_url"]
            networks_url = files_path["api_urls"]["eve_networks_url"]
            # FTD parameters
            ftd_node = files_path["urls"]["ftd_node_payload"]
            ftd_config = files_path["urls"]["ftd_config"]
            ftd_pwd = files_path["urls"]["ftd_pwd"]

            # FMC parameters
            fmc_token = files_path["fmc_api"]["fmc_token"]
            fmc_devices = files_path["fmc_api"]["fmc_devices"]
            fmc_data = files_path["urls"]["fmc_payload"]
            fmc_ha_payload = files_path["urls"]["ha_payload"]
            fmc_sec_zones_payload = files_path["urls"]["fmc_sec_zones"]
            fmc_interface_payload = files_path["urls"]["fmc_int_payload"]
            fmc_route_payload = files_path["urls"]["fmc_route_payload"]
            fmc_policyid_url = files_path["fmc_api"]["url_policyid"]
            fmc_device_details_url = files_path["fmc_api"]["dev_detail_url"]
            fmc_ha_settings_url = files_path["fmc_api"]["ha_settings_url"]
            fmc_sec_zones_url = files_path["fmc_api"]["sec_zones"]
            fmc_url_devcies_int_detail = files_path["fmc_api"]["url_devices_int_det"]
            fmc_obj_network_url = files_path["fmc_api"]["object_network"]
            fmc_obj_host_url = files_path["fmc_api"]["object_host"]
            fmc_routing_url = files_path["fmc_api"]["routing"]
            fmc_dev_int_url = files_path["fmc_api"]["url_devices_int"]
            fmc_ha_check_url = files_path["fmc_api"]["ha_check_url"]

    except FileNotFoundError:
        logger.error("The configuration file 'automation_urls.json' was not found.")
        raise FileNotFoundError("The configuration file 'automation_urls.json' was not found.")
        
    except json.JSONDecodeError:
        logger.error("The configuration file 'automation_urls.json' is invalid or malformed.")
        raise InvalidConfigurationError("The configuration file 'automation_urls.json' is invalid or malformed.")

    try:
        # Open the Excel file
        db_info = pd.read_excel(
            database_file,
            sheet_name=None,
            na_values=[],
            keep_default_na=False
    )
    except FileNotFoundError:
        logger.error(f"The Excel file '{database_file}' was not found.")
        raise FileNotFoundError(f"The Excel file '{db_info}' was not found.")
    except ValueError:
        logger.error(f"The Excel file '{database_file}' is invalid or malformed.")
        raise InvalidDataError(f"The Excel file '{db_info}' is missing required sheets or data.")
    
    try:
        # Extract data from Excel sheets
        data = {
            "creds": db_info['creds'][["Device type", "Host", "Username", "Password", "Secret"]].dropna().to_dict(orient="records") 

        }
    except KeyError as e:
        logger.error(f"Missing required data in the Excel file: {e}")
        raise InvalidDataError(f"Missing required data in the Excel file: {e}")
    try:
        # Open the JSON files with devices eve_ng payload

        with open(ftd_node, 'r') as ftd_payload_file:
                    
            ftd_payload = json.load(ftd_payload_file)
    except FileNotFoundError:
        logger.error(f"The file '{ftd_node}' was not found.")
        raise FileNotFoundError(f"The file '{ftd_node}' was not found.")
    try:
        # Open the JSON files with devices ha payload
        with open(fmc_ha_payload, 'r') as ha_payload_file:
            ha_settings = json.load(ha_payload_file)
    except FileNotFoundError:
        print(f"The file '{fmc_ha_payload}' was not found.")
        #logger.error(f"The file '{ha_file}' was not found.")
        raise FileNotFoundError(f"The file '{fmc_ha_payload}' was not found.") 
    try:
        # Open the JSON files with devices zone payload
        with open(fmc_sec_zones_payload, 'r') as sec_zone_payload_file:
            sec_zone_settings = json.load(sec_zone_payload_file)
    except FileNotFoundError:
        print(f"The file '{fmc_sec_zones_payload}' was not found.")
        #logger.error(f"The file '{ha_file}' was not found.")
        raise FileNotFoundError(f"The file '{fmc_sec_zones_payload}' was not found.") 
    try:
        # Open the JSON files with devices interfaces payload
        with open(fmc_interface_payload, 'r') as fmc_int_payload_file:
            fmc_int_settings = json.load(fmc_int_payload_file)
    except FileNotFoundError:
        print(f"The file '{fmc_interface_payload}' was not found.")
        #logger.error(f"The file '{ha_file}' was not found.")
        raise FileNotFoundError(f"The file '{fmc_interface_payload}' was not found.") 
    try:
        # Open the JSON files with device route payload
        with open(fmc_route_payload, 'r') as fmc_route_payload_file:
            fmc_route_settings = json.load(fmc_route_payload_file)
    except FileNotFoundError:
        print(f"The file '{fmc_route_payload}' was not found.")
        #logger.error(f"The file '{ha_file}' was not found.")
        raise FileNotFoundError(f"The file '{fmc_route_payload}' was not found.") 
    try:
        # Open the Excel file
        fmc_db_data = pd.read_excel(
            fmc_data,
            sheet_name='fmc_dev_data',
            na_values=[],
            keep_default_na=False
    )
    except FileNotFoundError:
        logger.error(f"The Excel file '{fmc_data}' was not found.")
        raise FileNotFoundError(f"The Excel file '{fmc_db_data}' was not found.")
    except ValueError:
        logger.error(f"The Excel file '{fmc_data}' is invalid or malformed.")
        raise InvalidDataError(f"The Excel file '{fmc_db_data}' is missing required sheets or data.")
    
    try:
        # Extract data from Excel sheets
        required_columns = ["type", "name", "hostName", "regKey", "accessPolicy"]
        if not all(col in fmc_db_data.columns for col in required_columns):
            raise ValueError(f"Missing required columns in the Excel file: {required_columns}")

        fmc_payload = {
            "device_payload": fmc_db_data[required_columns]
            .dropna()
            .apply(
                lambda row: { 
                    "type": row["type"],
                    "name": row["name"],
                    "hostName": row["hostName"],
                    "regKey": row["regKey"],
                    "accessPolicy": {"type": row["accessPolicy"]}
                },
                axis=1
            )
            .tolist()
        }
                
    except KeyError as e:
        logger.error(f"Missing required data in the Excel file: {e}")
        raise InvalidDataError(f"Missing required data in the Excel file: {e}")


    return data, \
        ftd_payload, \
        ftd_config, \
        ftd_pwd,\
        eve_ng_url_login,\
        eve_node_creation_url,\
        eve_authorization_header,\
        eve_start_nodes_url,\
        eve_node_port,\
        eve_interface_connection,\
        networks_url,\
        node_interface,\
        network_mgmt, \
        fmc_token,\
        fmc_devices,\
        fmc_payload, \
        ha_settings, \
        sec_zone_settings, \
        fmc_int_settings, \
        fmc_route_settings, \
        fmc_policyid_url, \
        fmc_device_details_url, \
        fmc_ha_settings_url, \
        fmc_sec_zones_url, \
        fmc_url_devcies_int_detail, \
        fmc_obj_network_url, \
        fmc_obj_host_url, \
        fmc_routing_url , \
        fmc_dev_int_url, \
        fmc_ha_check_url


def gather_valid_creds(creds):
    """
    Process and separate device credentials from a list of dictionaries.

    This function validates and processes a list of device credential dictionaries,
    typically loaded from an Excel sheet. It separates credentials for EVE-NG API
    access and FMC access, ensuring all required fields are present and properly structured.

    Steps:
    1. Validates that the input is a list of dictionaries.
    2. Iterates over each credential entry and checks for required keys.
    3. Adds the "secret" field if present.
    4. Separates credentials into EVE-NG API and FMC lists based on device type.
    5. Returns two lists: one for EVE-NG API credentials and one for FMC credentials.

    Args:
        creds (list): A list of dictionaries, each representing a device's credentials.

    Returns:
        tuple: A tuple containing two lists:
            - eve_API_creds (list): Credentials for EVE-NG API access.
            - fmc_creds (list): Credentials for FMC access.

    Raises:
        ValueError: If the input is not a list or required keys are missing.
        Exception: For any other errors encountered during processing.
    """
    try:
        # Validate input
        if not isinstance(creds, list):
            logger.error("The 'creds' input must be a list of dictionaries.")
            raise ValueError("The 'creds' input must be a list of dictionaries.")

        # Initialize lists for FTD and Linux devices
        eve_API_creds = []
        fmc_creds = []

        # Iterate over the credentials data
        for row in creds:
            # Validate required keys
            required_keys = ["Device type", "Host", "Username", "Password"]
            for key in required_keys:
                if key not in row:
                    logger.error(f"Missing required key '{key}' in credentials data.")
                    raise ValueError(f"Missing required key '{key}' in credentials data.")

            # Create a device dictionary
            device = {
                "device_type": row["Device type"],
                "host": row["Host"],
                "username": row["Username"],
                "password": row["Password"],
            }
            # Add the "secret" field if it exists
            if "Secret" in row and row["Secret"]:
                device["secret"] = row["Secret"]
            # Separate devices based on their type
            if row["Device type"] == "eve_ng":
                eve_API_creds.append(device) 
            if row["Device type"] == "fmc":
                fmc_creds.append(device)
        return eve_API_creds, fmc_creds
    except ValueError as e:
        logger.error(f"Invalid data in the credentials: {e}")
        raise ValueError(f"Invalid data in the credentials: {e}")
    except Exception as e:
        logger.error(f"An error occurred while processing credentials: {e}")
        raise Exception(f"An error occurred while processing credentials: {e}")