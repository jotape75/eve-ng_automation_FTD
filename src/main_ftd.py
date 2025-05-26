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
from utils_ftd import file_path, gather_valid_creds, display_message, color_text
from processing_ftd import user_auth, run_threads, threading_process,create_network_HA
from processing_fmc import fmc_register
import datetime
import sys
import os
import threading
from twisted.internet import reactor
from queue import Queue
from tqdm import tqdm

tqdm._instances.clear()

# Configure logging
timestamp = datetime.datetime.now()
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") # Format the timestamp for the log file name for LINUX
#formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Format the timestamp for the log file name for WINDOWS

LOG_FILE = f'/home/user/pystudies/myenv/pythonbasic/projects/eve-ng_automation_FTD/log/{formatted_timestamp}_main_log_file.log'  # Specify the log file path
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

    # Define the nodes to be created
    # Each dictionary represents a node type and the number of instances to create
    # Uncomment the nodes you want to deploy.
    # Make sure the number of nodes matches with the number of sheets in the Excel file.
    nodes = [
        {'FTD Firewall': 2}
    ]
    total_nodes = nodes[0]["FTD Firewall"]

    try:
        # Display the introductory message
        colors = color_text()  # Get color codes
        message = display_message(colors)
        print()
        print(message)

        # Load configuration and credentials
        (
        data, 
        ftd_payload, 
        ftd_config, 
        ftd_pwd,
        eve_ng_url_login,
        eve_node_creation_url,
        eve_authorization_header,
        eve_start_nodes_url,
        eve_node_port,
        eve_interface_connection,
        networks_url,
        node_interface,
        network_mgmt,
        fmc_token,
        fmc_devices,
        fmc_payload,
        ha_settings,
        sec_zone_settings,
        fmc_int_settings,
        fmc_route_settings,
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

        ) = file_path()
        # Authenticate with EVE-NG
        eve_API_creds,fmc_creds = gather_valid_creds(data["creds"])
        response, headers = user_auth(
            eve_API_creds, 
            eve_ng_url_login, 
            eve_authorization_header, 
            colors
        )
        # Create network ID for High Availability (HA)
        HA_network_id = create_network_HA(response,networks_url)
        # Run threads for node creation and configuration
        (
        createnode_queue,
        starnode_queue,
        connectnode_queue,
        configure_queue,
        closeconnection_queue
        ),fmc_register_queue,fmc_ha_queue,fmc_sec_zones_queue,fmc_interface_queue,fmc_object_host_queue,fmc_route_queue = run_threads(
            nodes,
            response,
            threading_process,
            headers, 
            ftd_payload, 
            ftd_config, 
            ftd_pwd,
            eve_node_creation_url,
            eve_start_nodes_url,
            eve_node_port,
            eve_interface_connection,
            node_interface,
            network_mgmt,
            colors,
            HA_network_id
        )
        print(f'\n{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}')
        print(f'{colors.get("green")}Registering {total_nodes} FTD devices to FMC...{colors.get("reset")}')
        print(f'{colors.get("blue")}' + '-' * 50 + f'{colors.get("reset")}\n')
        fmc_register_queue = Queue()

        fmc_register(
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
        )

        # Add a separator
        print()
        print(f'\n{colors.get("green")}' + '-' * 50 + f'{colors.get("reset")}')
        print(f'{colors.get("blue")}Task Results:{colors.get("reset")}')
        print(f'{colors.get("green")}' + '-' * 50 + f'{colors.get("reset")}')

        # Print the output from the queues in order
        print(f'\n{colors.get("blue")}#### NODE CREATION MESSAGE ####{colors.get("reset")}')
        while not createnode_queue.empty():
            print(createnode_queue.get())

        print(f'\n{colors.get("blue")}#### NODE START MESSAGE ####{colors.get("reset")}')
        while not starnode_queue.empty():
            print(starnode_queue.get())

        print(f'\n{colors.get("blue")}#### NODE CONNECTION MESSAGE ####{colors.get("reset")}')
        while not connectnode_queue.empty():
            print(connectnode_queue.get())

        print(f'\n{colors.get("blue")}#### NODE CONFIGURATION MESSAGE ####{colors.get("reset")}')
        while not configure_queue.empty():
            print(configure_queue.get())
        
        print(f'\n{colors.get("blue")}#### NODE CLOSURE MESSAGE ####{colors.get("reset")}')
        while not closeconnection_queue.empty():
            print(closeconnection_queue.get())

        print(f'\n{colors.get("blue")}#### FMC REGISTRATION MESSAGE ####{colors.get("reset")}')
        while not fmc_register_queue.empty():
            print(fmc_register_queue.get())

        print(f'\n{colors.get("blue")}#### HA REGISTRATION MESSAGE ####{colors.get("reset")}')
        while not fmc_ha_queue.empty():
            print(fmc_ha_queue.get())

        print(f'\n{colors.get("blue")}#### SECURITY ZONE CREATION MESSAGE ####{colors.get("reset")}')
        while not fmc_sec_zones_queue.empty():
            print(fmc_sec_zones_queue.get())
            
        print(f'\n{colors.get("blue")}#### INTERFACE CONFIGURATION MESSAGE ####{colors.get("reset")}')
        while not fmc_interface_queue.empty():
            print(fmc_interface_queue.get())
        print(f'\n{colors.get("blue")}#### HOST OBJ CONFIGURATION MESSAGE ####{colors.get("reset")}')
        while not fmc_object_host_queue.empty():
            print(fmc_object_host_queue.get())
        print(f'\n{colors.get("blue")}#### DEFAULT ROUTE CONFIGURATION MESSAGE ####{colors.get("reset")}')
        while not fmc_route_queue.empty():
            print(fmc_route_queue.get())

    except KeyboardInterrupt:
        logging.info("Program interrupted by user. Exiting...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
    
    
    # Stop the Twisted Reactor
        try:
            if reactor.running:
                reactor.callFromThread(reactor.stop)
                logging.info("Twisted Reactor forcefully stopped.")
        except Exception as e:
            logging.error(f"Error stopping Twisted Reactor: {e}")

        # Log and join all threads
        logging.debug(f"Active threads before exit: {threading.enumerate()}")
        for thread in threading.enumerate():
            if thread is not threading.main_thread() and not thread.daemon:
                logging.debug(f"Joining thread: {thread.name}")
                thread.join(timeout=5)
                if thread.is_alive():
                    logging.warning(f"Thread {thread.name} did not stop.")

        # Exit the program
        logging.info("Program exiting cleanly.")
       # sys.exit(0)



if __name__ == "__main__":
    main()