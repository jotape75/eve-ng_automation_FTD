import requests 
import json
import datetime
from queue import Queue
from tqdm import tqdm # Progress bar library for terminal output
import logging
import time

logger = logging.getLogger()


class FTDFirewall_HA:
    def __init__(
        self,
        fmc_creds_payload,
        fmc_token_api,
        fmc_policyid_url,
        fmc_devices_payload,
        colors
    ):

        self.fmc_creds_payload = fmc_creds_payload
        self.fmc_token_api = fmc_token_api
        self.fmc_policyid_url = fmc_policyid_url
        self.fmc_devices_payload = fmc_devices_payload

        self.colors = colors

        self.username = self.fmc_creds_payload[0]['username']
        self.password = self.fmc_creds_payload[0]['password']
        self.headers = {"Content-Type": "application/json"}

        self.total_devices = len(self.fmc_creds_payload)

        self.get_api_key = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Getting API Keys{colors.get("reset")}', position=0, leave=True, ncols=100)
        self.config_int = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Enabling Interfaces for HA{colors.get("reset")}', position=1, leave=True, ncols=100)
        self.commit_interfaces = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Commit Changes - HA Interfaces{colors.get("reset")}', position=2, leave=True, ncols=100)
        self.enable_ha = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Enable HA{colors.get("reset")}', position=3, leave=True, ncols=100)
        self.commit_ha = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Commit Changes- HA Config{colors.get("reset")}', position=4, leave=True, ncols=100)

    def get_api_keys(self):
            
        try:
            requests.packages.urllib3.disable_warnings()
            # Generate Token
            response_token = requests.post(self.fmc_token_api, headers=self.headers, auth=(self.username, self.password), verify=False)
            response_token.raise_for_status()
            # Extract tokens from headers
            auth_token = response_token.headers.get("X-auth-access-token", None)
            if not auth_token:
                raise Exception("Authentication token not found in response.")
            logger.info(f"Authentication successful! Token: {auth_token}")
            self.headers["X-auth-access-token"] = auth_token  
            self.get_api_key.update(1) # Update progress bar for getting API keys
        except requests.exceptions.RequestException as e:
            logger.error(f"Error: {e}")
        return self.headers
    def register_device(self):
        response_policy = requests.get(self.fmc_policyid_url, headers=self.headers, verify=False)
        response_policy.raise_for_status()
        policies = response_policy.json().get('items', []) # List of policies
        policy_id = None
        for policy in policies:
            if policy["name"] == "Initial_policy":
                policy_id = policy["id"]
                break

        if not policy_id:
            logger.info("Initial_policy not found.")
            return

        # Assign policy ID to each device
        for device in self.fmc_devices_payload["device_payload"]:
            device["accessPolicy"]["type"] = policy_id
            logger.info(f"Assigned policy ID {policy_id} to device {device['name']}")