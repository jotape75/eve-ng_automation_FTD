"""
Main script for EVE-NG automation.

This script automates the deployment and initial configuration of Cisco FTD (Firepower Threat Defense) devices in an EVE-NG environment, 
and registers them to Cisco FMC (Firepower Management Center) using the FMC API. 

Key features:
- Handles authentication, node creation, and device configuration through multithreading for efficiency.
- Automates network and HA (High Availability) setup.
- Registers FTD devices to FMC and performs initial interface and security zone configuration via the FMC API.
- Collects and displays progress and results using message queues and progress bars.
- Designed for extensibility and scalable lab or production deployments.

GitHub: https://github.com/jotape75

"""

import logging
from utils_ftd import file_path,display_message, color_text
from ftd_automation_ha import FTDFirewall_HA
import datetime
from tqdm import tqdm



# Configure logging
timestamp = datetime.datetime.now()
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") # Format the timestamp for the log file name for LINUX
#formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Format the timestamp for the 
# log file name for WINDOWS

LOG_FILE = f'/home/user/pystudies/myenv/pythonbasic/projects/FTD_automation_deploy/log/{formatted_timestamp}_main_log_file.log'  # Specify the log file path
logging.basicConfig(
    filename=LOG_FILE,  # Log file
    level=logging.DEBUG,  # Log level (DEBUG captures all levels)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format
)

def main():

    """
    Main function to execute the EVE-NG automation workflow.

    This function orchestrates the entire process of automating the deployment
    of multiple vendor devices in EVE-NG. It performs the following tasks:

    1. Displays an introductory message:
        - Calls `color_text()` to retrieve color codes for styling.
        - Calls `display_message(colors)` to display an ASCII art banner and project details.

    2. Loads configuration and credentials:
        - Calls `file_path()` to load configuration files, device payloads, API URLs, and other details.

    3. Authenticates with the EVE-NG API:
        - Calls `gather_valid_creds(data["creds"])` to retrieve valid credentials.
        - Calls `user_auth(eve_API_creds, eve_ng_url_login, eve_authorization_header, colors)` 
          to authenticate with the EVE-NG API and obtain a session token.

    4. Deploys and configures devices:
        - Calls `run_threads()` to handle the creation, starting, connecting, and configuration 
          of devices in EVE-NG using multithreading.

    Args:
        None

    Returns:
        None
    """
    try:
        # Display the introductory message
        colors = color_text()  # Get color codes
        message = display_message(colors)
        print()
        print(message)

        # Load configuration and credentials
        
        fmc_creds_payload,fmc_token_api = file_path()


        firewall_deployer_ha = FTDFirewall_HA(fmc_creds_payload, fmc_token_api, colors)
        # Get API keys
        firewall_deployer_ha.get_api_keys()

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)  


if __name__ == "__main__":
    main()