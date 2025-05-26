"""
eve_api.py

This script interacts with the EVE-NG API to authenticate a user and retrieve data from a specified endpoint. 
It demonstrates how to use Python's `requests` library to make HTTP requests and handle JSON responses.

Functions:
-----------
1. get_data(data):
    - Accepts a dictionary and pretty-prints it as a JSON-formatted string.
    - Useful for debugging and visualizing API responses.

2. user_auth():
    - Authenticates the user with the EVE-NG API using a POST request.
    - Returns the response object containing authentication cookies if successful.
    - Exits the script if authentication fails.

Main Execution:
---------------
- Authenticates the user with the EVE-NG API.
- Makes a GET request to retrieve network data from the specified lab (`Ansiblelab.unl`).
- Pretty-prints the retrieved data using the `get_data` function.

Dependencies:
-------------
- requests: For making HTTP requests.
- json: For handling JSON data.
- csv: (Imported but not used in this script.)
- pprint: For pretty-printing JSON responses.

Usage:
------
Run the script directly to authenticate with the EVE-NG API and retrieve network data:
    python eve_api.py

Note:
-----
Ensure the EVE-NG server is running and accessible at the specified URL.
Update the `username`, `password`, and url and `data_url` variables as needed for your environment.
"""

import requests # Import the requests module.
import json # Import the json module.
import csv # Import the csv module.
from pprint import pprint # Import the pprint module for pretty-printing.
import time

def get_data(data): # Define a function that will make a GET request to a REST API and save the response to a JSON file.
    print ()

    json_string = json.dumps(data, indent=4) # Converts the dictionary to a JSON-formatted string with indentation. Only useful
    #for printing. Use the response.json() for getting the real dict format.
    print(json_string) 
    print(type(json_string))
    print ()

def user_auth():

    url = 'http://192.168.0.119/api/auth/login'
    
    # Define the payload with the username and password
    login_payload = {
    'username': 'admin',
    'password': 'eve',
    'html5': '-1'
    }



    response = requests.post(url, json=login_payload)

    if response.status_code == 200:
        print('Logging to ', url)
        print('Login successful')
    else:
        print('Login failed')
        pprint(response.text)
        exit()
    return response
if __name__ == "__main__":
    
    # Define the device IDs for which you want to create connections
    device_id = ["14", "15"]
    # Define the payload for creating a network in EVE-NG
    network_payload = {
    "type": "bridge",
    "name": "ha_connection",
    "left": 100,
    "top": 100,
    "visibility": 1
    }
    headers = {
        'Authorization': "Basic YWRtaW46ZXZl",
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    response = user_auth()
    links_url = 'http://192.168.0.119/api/labs/Ansiblelab.unl/links'
    topology_url = 'http://192.168.0.119/api/labs/Ansiblelab.unl/topology'
    conn_creation = "http://192.168.0.119/api/labs/Ansiblelab.unl/nodes/{device_id}/interfaces"

    networks_url = 'http://192.168.0.119/api/labs/Ansiblelab.unl/networks'
    net_response = requests.post(networks_url, json=network_payload, cookies=response.cookies)
    print("Network POST status:", net_response.status_code)
    print("Network POST response:", net_response.text)
    network_id = net_response.json()["data"]["id"]

    interfaces = json.dumps({"7": network_id}) #7 is the index of the interface G0/5
    for device in device_id:
        response1 = requests.put(
        conn_creation.format(device_id=device),
        data=interfaces,
        headers=headers,
        cookies=response.cookies
    )
        print("Connection creation status code:", response1.status_code)
        print("Connection creation response:", response1.text)