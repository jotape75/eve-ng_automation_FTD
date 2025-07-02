import json
import pandas as pd # Data manipulation library
from exceptions_ftd import FileNotFoundError, InvalidConfigurationError, InvalidDataError
import pyfiglet # ASCII art library
import logging

logger = logging.getLogger()


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
        with open('/home/user/pystudies/myenv/pythonbasic/projects/FTD_automation_deploy/data/automation_urls_ftd.json', 'r') as config_file:
            files_path = json.load(config_file)

            # FMC parameters
            fmc_creds = files_path["payload"]["fmc_creds_payload"]
            fmc_token_api = files_path["fmc_api"]["fmc_token_api"]
            # fmc_devices = files_path["fmc_api"]["fmc_devices"]
            # fmc_data = files_path["urls"]["fmc_payload"]
            # fmc_ha_payload = files_path["urls"]["ha_payload"]
            # fmc_sec_zones_payload = files_path["urls"]["fmc_sec_zones"]
            # fmc_interface_payload = files_path["urls"]["fmc_int_payload"]
            # fmc_route_payload = files_path["urls"]["fmc_route_payload"]
            # fmc_policyid_url = files_path["fmc_api"]["url_policyid"]
            # fmc_device_details_url = files_path["fmc_api"]["dev_detail_url"]
            # fmc_ha_settings_url = files_path["fmc_api"]["ha_settings_url"]
            # fmc_sec_zones_url = files_path["fmc_api"]["sec_zones"]
            # fmc_url_devcies_int_detail = files_path["fmc_api"]["url_devices_int_det"]
            # fmc_obj_network_url = files_path["fmc_api"]["object_network"]
            # fmc_obj_host_url = files_path["fmc_api"]["object_host"]
            # fmc_routing_url = files_path["fmc_api"]["routing"]
            # fmc_dev_int_url = files_path["fmc_api"]["url_devices_int"]
            # fmc_ha_check_url = files_path["fmc_api"]["ha_check_url"]

    except FileNotFoundError:
        logger.error("The configuration file 'automation_urls.json' was not found.")
        raise FileNotFoundError("The configuration file 'automation_urls.json' was not found.")
        
    except json.JSONDecodeError:
        logger.error("The configuration file 'automation_urls.json' is invalid or malformed.")
        raise InvalidConfigurationError("The configuration file 'automation_urls.json' is invalid or malformed.")
        

    try:
        # Open the JSON files with devices ha payload
        with open(fmc_creds, 'r') as file_0:
            fmc_creds_payload = json.load(file_0)
    except FileNotFoundError:
        raise FileNotFoundError(f" file not found: {files_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid XML in file: {files_path}")


    return fmc_creds_payload,fmc_token_api

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
    cyan = "\033[1;36m"
    reset = "\033[0m"
    colors = {
        "green": green,
        "red": red,
        "yellow": yellow,
        "blue": blue,
        "cyan": cyan,
        "reset": reset
    }
    return colors