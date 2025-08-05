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
        fmc_devices_api,
        dev_detail_url_api,
        colors
    ):

        self.fmc_creds_payload = fmc_creds_payload
        self.fmc_token_api = fmc_token_api
        self.fmc_policyid_url = fmc_policyid_url
        self.fmc_devices_payload = fmc_devices_payload
        self.fmc_devices_api = fmc_devices_api
        self.dev_detail_url_api = dev_detail_url_api
        self.device_name = []
        self.device_names = []
        self.ready_devices = {}


        self.colors = colors

        self.username = self.fmc_creds_payload[0]['username']
        self.password = self.fmc_creds_payload[0]['password']
        self.headers = {"Content-Type": "application/json"}

        self.total_devices = len(self.fmc_creds_payload)

        self.get_api_key = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Getting API Keys{colors.get("reset")}', position=0, leave=True, ncols=100)
        self.fmc_register_progress = tqdm(total=self.total_devices, desc=f'{colors.get("cyan")}Registering Devices on FMC{colors.get("reset")}', position=1, leave=True, ncols=100)
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
        try:
            poll_interval = 10
            waited = 0
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
                device["accessPolicy"]["id"] = policy_id
                logger.info(f"Assigned policy ID {policy_id} to device {device['name']}")
            
            ### REGISTER DEVICES TO FMC ###

            for device in self.fmc_devices_payload["device_payload"]:
                self.device_name = device["name"]
                response_device = requests.post(self.fmc_devices_api, headers=self.headers, data=json.dumps(device), verify=False)
                if response_device.status_code == 202:
                    logger.info(f"Device {self.device_name} added successfully.")
                else:
                    logger.info(f"Failed to add device {self.device_name}. Status code: {response_device.status_code}")
                    logger.info(response_device.text)
            for name in self.fmc_devices_payload["device_payload"]:
                self.device_names.append(name['name'])
            # Wait for all devices to appear in FMC device records
            max_wait = 600  # seconds
            waited_rec = 0 
            poll_interval = 10 
            pool_interval_reg = 30
            while True:
                response_show = requests.get(self.fmc_devices_api, headers=self.headers, verify=False)
                response_show.raise_for_status()
                devices = response_show.json().get('items', [])
                found_device_names = [dev["name"] for dev in devices]
                missing_devices = set(self.device_names) - set(found_device_names)
                if not missing_devices:
                    logger.info("All devices have appeared in FMC device records.")
                    break
                if waited_rec > max_wait:
                    logger.error(f"Timeout: Devices {missing_devices} did not appear in FMC device records after {max_wait} seconds.")
                    return
                logger.info(f"Waiting for devices to appear in FMC: {missing_devices} ({waited_rec}s)")
                time.sleep(poll_interval)
                waited_rec += poll_interval
            while True:
                response_health_status = requests.get(self.fmc_devices_api, headers=self.headers, verify=False)
                response_health_status.raise_for_status()
                devices = response_health_status.json().get('items', [])
                for dev in devices:
                    if dev["name"] in self.device_names:
                        detail_resp = requests.get(self.dev_detail_url_api.format(device_id=dev['id']), headers=self.headers, verify=False)
                        detail_resp.raise_for_status()
                        dev_detail = detail_resp.json()
                        health = dev_detail.get("healthStatus", "").lower()
                        deploy = dev_detail.get("deploymentStatus", "").upper()
                        logger.info(f"Device {dev['name']} healthStatus: {health}, deploymentStatus: {deploy}")
                        healthy_states = ["green", "yellow", "recovered"]
                        if health in healthy_states and deploy == "DEPLOYED" and dev["name"] not in self.ready_devices:
                            self.ready_devices[dev["name"]] = dev
                            self.fmc_register_progress.update(1)
                        if health == "red" and deploy == "NOT_DEPLOYED":
                            logger.info(f"Device {dev['name']} is not deployed. Please check logs...")
                            continue
                if missing_devices:
                    logger.error(f"Device(s) {missing_devices} are no longer present in FMC device records. Registration or deployment likely failed.")
                    break
                if len(self.ready_devices) == len(self.device_names):
                    logger.info("All devices are ready and deployed!")
                    break
                if waited > 1800:  # 30 minutes, just as a warning
                    logger.info(f"Warning: Devices are taking longer than expected to be ready. Waited {waited} seconds.")
                logger.info(f"Waiting... ({waited}s)")
                time.sleep(pool_interval_reg)
                waited += pool_interval_reg

            if len(self.ready_devices) < len(self.device_names):
                logger.info("Timeout waiting for devices to be ready.")
                return
        except requests.exceptions.RequestException as e:
            logger.error(f"Error: {e}")
        