# **🔥 End-to-End Cisco FTD Automation: EVE-NG Node Creation to FMC Configuration**

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/jotape75/eve-ng_automation_FTD)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![GitHub stars](https://img.shields.io/github/stars/jotape75/eve-ng_automation_FTD?style=social)


This project automates the deployment and configuration of **Cisco Firepower Threat Defense (FTD)** devices in **EVE-NG** and their registration with **Firepower Management Center (FMC)** using Python. It supports multithreading for efficient handling of tasks like node creation, device registration, HA configuration, security zones, interfaces, and routing.

---

## **Features**

- **FTD Device Automation**: Automates deployment of Cisco FTD devices in EVE-NG.
- **FMC Integration**: Automatically registers FTD devices with Firepower Management Center via RESTful API.
- **High Availability Configuration**: Sets up HA pairs for FTD devices via RESTful API.
- **Security Zone Management**: Creates and assigns security zones to interfaces via RESTful API.
- **Interface Configuration**: Configures physical interfaces with IP addresses and security zones via RESTful API..
- **Routing Configuration**: Creates host objects and default static routes via RESTful API..
- **Multithreading**: Speeds up the process by handling multiple tasks concurrently.
- **Dynamic Configuration**: Reads device credentials and configurations from external JSON files.
- **Progress Tracking**: Real-time progress bars for monitoring automation tasks.
- **Error Handling**: Includes robust exception handling for better debugging.
- **VNC & OCR Integration**: Uses VNC and OCR (optical Character Recognition) for device console automation.

---

## **Project Structure**

```
eve-ng_automation_FTD
├── data
│   ├── automation_urls_ftd.json
│   ├── eve_creds.xlsx
│   ├── fmc_dev_data.xlsx
│   ├── ftd_pwd.txt
│   ├── FTD.xlsx
│   └── payload
│       ├── default_route.json
│       ├── fmc_ha_payload.json
│       ├── ftd_node.json
│       ├── interface.json
│       └── sec_zones.json
├── EVE-NG_VM_SETUP.md
├── LICENSE
├── log
│   └── README.md
├── README.md
├── requirements.txt
├── src
│   ├── exceptions_ftd.py
│   ├── main_ftd.py
│   ├── processing_fmc.py
│   ├── processing_ftd.py
│   ├── __pycache__
│   │   ├── exceptions_ftd.cpython-310.pyc
│   │   ├── processing_fmc.cpython-310.pyc
│   │   ├── processing_ftd.cpython-310.pyc
│   │   └── utils_ftd.cpython-310.pyc
│   └── utils_ftd.py
└── troubleshooting
    ├── eve_api_connection_test.py
    └── fmc_api_connection_test.py
```
---
## **Installation**

### **Prerequisites**

**System Requirements:**
- **Python 3.8 - 3.12** (See compatibility notes below)
- **Git** (for cloning the repository)
- **Tesseract OCR** (for text recognition from screenshots)

### **Python Version Compatibility**

| Python Version | Status | Notes |
|----------------|--------|-------|
| 3.8 - 3.12 | ✅ Fully Supported | Recommended versions |
| 3.13+ | ⚠️ Requires Setup | Install `telnetlib3`: `pip install telnetlib3` |

### **Windows Setup Guide**

**Prerequisites:**
- **Python 3.8-3.12** (Python 3.13+ requires additional setup)
- **Git** (for cloning the repository)
- **Tesseract OCR** (for text recognition from screenshots)

### **Step-by-Step Windows Installation**

#### **1. Install Tesseract OCR**
```cmd
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Run installer as Administrator
# Default installation path: C:\Program Files\Tesseract-OCR\
```

#### **2. Clone Repository**
```cmd
# Clone the repository
git clone https://github.com/your-username/eve-ng_automation_FTD.git
cd eve-ng_automation_FTD
```

#### **3. Create Virtual Environment**
```cmd
# Create virtual environment (use Command Prompt, not PowerShell)
python -m venv venv311

# Activate virtual environment
venv311\Scripts\activate.bat

# Verify activation (should show (venv311) prefix)
```

#### **4. Install Dependencies**
```cmd
# Install required packages
pip install -r requirements.txt
```
#### **5. Configure Tesseract**
```cmd
# Add Tesseract to PATH for current session
set PATH=%PATH%;C:\Program Files\Tesseract-OCR\

# Verify Tesseract installation
tesseract --version

# Test Python integration
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"
```

#### **6. Run the Automation**
```cmd
# Run the complete automation
python src\main_ftd.py
```

### **Linux setup Guide**

**Install Tesseract OCR:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr

# CentOS/RHEL
sudo yum install tesseract

# macOS
brew install tesseract

```

### **Setup Steps**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jotape75/eve-ng_automation_FTD.git
   ```

2. **Navigate to the project directory:**
   ```bash
   cd eve-ng_automation_FTD
   ```

3. **Fix file permissions (Linux/Mac only):**
   ```bash
   # Ensure you own all project files
   sudo chown -R $USER:$USER ./
   
   # Set proper directory permissions
   find . -type d -exec chmod 755 {} \;
   
   # Set proper file permissions
   find . -type f -exec chmod 644 {} \;
   
   # Make Python scripts executable
   chmod +x src/*.py
   ```

4. **Create and activate a virtual environment (recommended):**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On Linux/Mac:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

5. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Verify installation:**
   ```bash
   # Test Python dependencies
   python -c "import requests, pandas, vncdotool, pytesseract; print('All dependencies installed successfully!')"
   
   # Test Tesseract OCR
   tesseract --version
   
   # Test script execution
   python src/main_ftd.py --help
   ```

### **Important Notes**

⚠️ **Always run the automation as your regular user, not as root:**

```bash
# ❌ DON'T do this:
sudo python src/main_ftd.py

# ✅ DO this instead:
python src/main_ftd.py
```

**Why?** Running as root creates files owned by root, causing permission conflicts when:
- VNC automation tries to save screenshots
- OCR processing creates temporary files
- Log files are written to the project directory

### **EVE-NG VM Environment Setup**

**⚠️ Important for EVE-NG Community Edition Users:**

If you're using the **EVE-NG Community Edition VM** (downloaded from EVE-NG website), you may encounter screen capture issues due to missing GUI automation dependencies.

**See the complete setup guide:** [EVE-NG_VM_SETUP.md](EVE-NG_VM_SETUP.md)

---

## **File Configuration**

### **1. Edit Credential File**:

**FTD Initial Configuration** (`data/FTD.xlsx`):
Create an Excel file with the following structure:

| Command |
|---------|
| manual |
| 192.168.0.221 |
| 255.255.255.0 |
| 192.168.0.1 |
| cisco_FTD_01 |
| 8.8.8.8,8.8.4.4 |
| mydomain.com |

**Configuration Order:**

1. **manual** - Configuration mode (manual setup)
2. **192.168.0.221** - Management IP address
3. **255.255.255.0** - Subnet mask
4. **192.168.0.1** - Default gateway
5. **cisco_FTD_01** - Device hostname
6. **8.8.8.8,8.8.4.4** - DNS servers (comma-separated)
7. **mydomain.com** - Domain name


**FTD Password Configuration** (`data/ftd_pwd.txt`):
Create a text file containing the FTD admin password:

```
Admin-FTD2025
```
**Important Notes:**
- **Keep the recommended password**: `Admin-FTD2025` is recommended due to VNC character input limitations
- **VNC Compatibility**: Some special characters may not be sent properly via VNC automation
- **Single Line**: The file should contain only the password on a single line

**EVE-NG and FMC API Credentials** (`data/eve_creds.xlsx`):

| Device type | Host | Username | Password | Secret |
|-------------|------|----------|----------|--------|
| eve_ng | 192.168.0.119 | admin | eve | |
| fmc | 192.168.0.201 | api_user | Cisco1234! | |

**Column Descriptions:**
- **Device type**: Type of device (eve_ng, fmc)
- **Host**: IP address or hostname of the device
- **Username**: API username for authentication
- **Password**: API password for authentication  
- **Secret**: Additional secret/token (if required, otherwise leave empty)

*FMC Device Registration** (`data/fmc_devices.xlsx`):
Create an Excel file with the following structure:

| type | name | hostName | regKey | accessPolicy |
|------|------|----------|--------|--------------|
| Device | ciscoftd01 | 192.168.0.221 | cisco123 | AccessPolicy |
| Device | ciscoftd02 | 192.168.0.222 | cisco123 | AccessPolicy |

**Column Descriptions:**
- **type**: Device type (typically "Device" for FTD devices)
- **name**: Device name as it will appear in FMC
- **hostName**: Management IP address of the FTD device
- **regKey**: Registration key for device authentication
- **accessPolicy**: Access control policy to assign to the device


### **3. Configure Automation Settings**:

📋 **Installation & dependencies are covered in the README.md installation section above. This section focuses only on the configuration files you need to customize for your environment.**

**Update Configuration File** (`data/automation_urls_ftd.json`):

**📦 EVE-NG API URLs** - Replace `<YOUR_EVE_NG_IP>` with your EVE-NG server IP:
```json
"api_urls": {
    "eve_ng_url_login": "http://<YOUR_EVE_NG_IP>/api/auth/login",
    "eve_node_creation_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/nodes",
    "eve_start_node_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/nodes/{device_id}/start",
    "eve_interface_connection_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/nodes/{device_id}/interfaces",
    "eve_node_port": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/nodes/{device_id}",
    "eve_node_interface_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/nodes/{device_id}/interfaces",
    "eve_network_mgmt_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/networks/<YOUR_NETWORK_MGMT_ID>",
    "eve_networks_url": "http://<YOUR_EVE_NG_IP>/api/labs/Ansiblelab.unl/networks"
}
```

**⚠️ Important Network Management Configuration:**

**Find Your Management Network ID:**
1. **Open EVE-NG Web Interface**
2. **Navigate to your lab** (Ansiblelab.unl)
3. **Right-click on management cloud** → **Edit**
4. **Note the Network ID** (e.g., 21, 1, 5, etc.)

*Modify the network management cloud ID in the api_urls dictionary as well as in the code 
for connection between the devices and network management work properly:

**Example Management Network URLs:**
```json
"eve_network_mgmt_url": "http://<YOUR EVE-NG IP ADDRESS>/api/labs/Ansiblelab.unl/networks/<YOUR NETWORK MGMT ID>"
```

**Update Processing File** (`src/processing_ftd.py`):

**Locate the `create_nodes` function and update the management network ID:**

```python
# Find this line in src/processing_ftd.py (around line XXX):
interfaces = '{"0":"<MGMT network ID>"}' #21 is the id of the management network being used on MY EVE-ng. Change it for your environment.
```
**🔍 How to Find Your Network Management ID:**

**Method  - EVE-NG Web Interface:**
1. **Login to EVE-NG** web interface
2. **Open your lab** (xxxx.unl)
3. **Right-click management cloud** → Edit
4. **Note the Network ID** displayed

**🔥 FMC API URLs** - Replace `<YOUR_FMC_IP>` with your FMC server IP:
```json
"fmc_api": {
    "fmc_token": "https://<YOUR_FMC_IP>/api/fmc_platform/v1/auth/generatetoken",
    "fmc_devices": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devices/devicerecords",
    "fmc_ha_pair": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs",
    "url_policyid": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/policy/accesspolicies",
    "dev_detail_url": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}",
    "ha_settings_url": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs",
    "url_devices_int": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devices/devicerecords/{device_id}/physicalinterfaces",
    "ha_check_url": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devicehapairs/ftddevicehapairs/{ha_id}",
    "sec_zones": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/object/securityzones",
    "url_devices_int_det": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devices/devicerecords/{primary_status_id}/physicalinterfaces/{interface_id}",
    "object_network": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/object/networks",
    "object_host": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/object/hosts",
    "routing": "https://<YOUR_FMC_IP>/api/fmc_config/v1/domain/default/devices/devicerecords/{primary_status_id}/routing/ipv4staticroutes"
}
```

**📁 File Paths** - Replace `<YOUR_PROJECT_PATH>` with your project directory:

**⚠️ Note for Windows Users:** Use forward slashes (/) even on Windows, as shown in the examples below.

```json
"urls": {
    "data_file": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/eve_creds.xlsx",
    "ftd_node_payload": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/payload/ftd_node.json",
    "ftd_config": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/FTD.xlsx",
    "ftd_pwd": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/ftd_pwd.txt",
    "screen_shot": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/log",
    "fmc_payload": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/fmc_dev_data.xlsx",
    "ha_payload": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/payload/fmc_ha_payload.json",
    "fmc_sec_zones": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/payload/sec_zones.json",
    "fmc_int_payload": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/payload/interface.json",
    "fmc_route_payload": "<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/payload/default_route.json"
}
```

**🔧 Additional File Updates:**

**Update Utils File** (`src/utils_ftd.py`):
```python
# Replace <YOUR_PROJECT_PATH> with your actual project path
with open('<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/data/automation_urls_ftd.json', 'r') as config_file:
    files_path = json.load(config_file)
```

**Update Main File** (`src/main_ftd.py`):
```python
# Update log file path and select correct timestamp format for your OS

# For Linux/Mac:
formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

# For Windows:
# formatted_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

LOG_FILE = f'<YOUR_PROJECT_PATH>/eve-ng_automation_FTD/log/{formatted_timestamp}_main_log_file.log'
```

**📋 Complete Configuration Checklist:**

1. ✅ **EVE-NG IP**: Replace `<YOUR_EVE_NG_IP>` in `api_urls` section
2. ✅ **FMC IP**: Replace `<YOUR_FMC_IP>` in `fmc_api` section  
3. ✅ **Project Path**: Replace `<YOUR_PROJECT_PATH>` in `urls` section
4. ✅ **Network Management ID**: Replace `<YOUR_NETWORK_MGMT_ID>` in `eve_network_mgmt_url`
5. ✅ **Processing File**: Update network ID in `src/processing_ftd.py` `create_nodes` function
6. ✅ **Utils File**: Update path in `src/utils_ftd.py`
7. ✅ **Main File**: Update log path in `src/main_ftd.py`
8. ✅ **Timestamp**: Select correct format for your OS

**🔧 Critical Network Configuration:**
- **Management Network ID must match** in both JSON config AND processing_ftd.py
- **Without correct network ID**, FTD devices won't have management connectivity
- **Test connectivity** after configuration changes

**💡 Example Paths:**
```
Linux:   /home/username/eve-ng_automation_FTD
Windows: C:/Users/username/eve-ng_automation_FTD
```

**High Availability Configuration** (`data/payload/fmc_ha_payload.json`):
```json

** There is no need to mofidy this file. **
{
    "ha_payload": {
        "type": "DeviceHAPair",
        "name": "ciscoftd_HA",
        "primary": {
            "id": "",
            "name": ""
        },
        "secondary": {
            "id": "",
            "name": ""
        },
        "ftdHABootstrap": {
            "isEncryptionEnabled": false,
            "useSameLinkForFailovers": true,
            "lanFailover": {
                "subnetMask": "255.255.255.248",
                "activeIP": "192.168.255.252",
                "standbyIP": "192.168.255.254",
                "logicalName": "lanFailover",
                "useIPv6Address": false,
                "interfaceObject": {
                    "id": "interface_id of 1st device",
                    "type": "PhysicalInterface",
                    "MTU": 1500,
                    "mode": "NONE",
                    "enabled": false,
                    "name": "GigabitEthernet0/5",
                    "priority": 0,
                    "managementOnly": false
                }
            },
            "statefulFailover": {
                "subnetMask": "255.255.255.248",
                "activeIP": "192.168.255.252",
                "standbyIP": "192.168.255.254",
                "logicalName": "statefulFailover",
                "useIPv6Address": false,
                "interfaceObject": {
                    "id": "interface_id of 2st device",
                    "type": "PhysicalInterface",
                    "MTU": 1500,
                    "mode": "NONE",
                    "enabled": false,
                    "name": "GigabitEthernet0/5",
                    "priority": 0,
                    "managementOnly": false
                }
            }
        },
        "ftdHAFailoverTriggerCriteria": {
            "noOfFailedInterfaceLimit": 1,
            "peerPollTimeUnit": "SEC",
            "peerPollTime": 1,
            "peerHoldTimeUnit": "SEC",
            "peerHoldTime": 15,
            "interfacePollTime": 5,
            "interfacePollTimeUnit": "SEC",
            "interfaceHoldTime": 25
        }
    }
}
```
**HA Configuration Fields:**
- **primary/secondary**: Device IDs and names (populated at runtime)
- **lanFailover**: LAN failover interface configuration
- **statefulFailover**: Stateful failover interface configuration
- **ftdHAFailoverTriggerCriteria**: Failover timing and trigger settings

**Security Zones** (`data/payload/sec_zones.json`):
```json
{
    "sec_zones_payload": [
      {
        "type": "SecurityZone",
        "name": "OUTSIDE-SEC_ZONE",
        "interfaceMode": "ROUTED"
      },
      {
        "type": "SecurityZone",
        "name": "INSIDE-SEC_ZONE",
        "interfaceMode": "ROUTED"
      },
      {
        "type": "SecurityZone",
        "name": "DMZ-SEC_ZONE",
        "interfaceMode": "ROUTED"
      }
    ]
  }

```
**Security Zone Configuration Fields:**
- **sec_zones_payload**: Array containing all security zones to be created
  - **type**: Object type (always "SecurityZone" for security zones)
  - **name**: Security zone name as it will appear in FMC
  - **interfaceMode**: Interface mode type (ROUTED, SWITCHED, or PASSIVE)

**Zone Index Reference:**
- **Index 0**: OUTSIDE-SEC_ZONE (for external/internet-facing interfaces)
- **Index 1**: INSIDE-SEC_ZONE (for internal/LAN interfaces)  
- **Index 2**: DMZ-SEC_ZONE (for DMZ/server interfaces)

**Interface Mode Options:**
- **ROUTED**: For Layer 3 routed interfaces (most common)

**Note:** The zone_index values in `interface_config.json` correspond to the array position of security zones in this file (0-based indexing).


**Interface Configuration** (`data/payload/interface_config.json`):
```json
{
    "GigabitEthernet0/0": {
      "ifname": "OUTSIDE",
      "ip_address": "10.20.20.100",
      "netmask": "255.255.255.0",
      "zone_index": 0
    },
    "GigabitEthernet0/1": {
      "ifname": "INSIDE",
      "ip_address": "10.10.10.100",
      "netmask": "255.255.255.0",
      "zone_index": 1
    },
    "GigabitEthernet0/2": {
      "ifname": "DMZ",
      "ip_address": "10.30.30.100",
      "netmask": "255.255.255.0",
      "zone_index": 2
    }
  }
```
**Interface Configuration Fields:**
- **GigabitEthernet0/X**: Physical interface name (Ethernet interface identifier)
  - **ifname**: Logical interface name as it appears in FMC
  - **ip_address**: Static IP address assigned to the interface
  - **netmask**: Subnet mask for the interface network
  - **zone_index**: Security zone assignment index (references sec_zones.json array position)

**Zone Index Mapping:**
- **zone_index 0**: Maps to first security zone in sec_zones.json (INSIDE_ZONE)
- **zone_index 1**: Maps to second security zone in sec_zones.json (OUTSIDE_ZONE)  
- **zone_index 2**: Maps to third security zone in sec_zones.json (DMZ_ZONE if configured)

**Note:** Ensure the zone_index values correspond to the correct security zones defined in your `sec_zones.json` file.

**Static Route Configuration** (`data/payload/default_route.json`):
```json
{
    "host_object": {
        "name": "outside_gw",
        "value": "10.20.20.1",
        "type": "host"
    },
    "static_route_payload": {
        "type": "IPv4StaticRoute",
        "name": "default_route",
        "interfaceName": "OUTSIDE",
        "selectedNetworks": [
            {
                "id": "",
                "type": "Network"
            }
        ],
        "gateway": {
            "object": {
                "id": "",
                "type": "Host"
            }
        },
        "metricValue": 1,
        "isTunneled": false
    }
}
```

**Configuration Fields:**
- **host_object**: Gateway host object configuration
  - **name**: Host object name in FMC
  - **value**: Gateway IP address
  - **type**: Object type (host)
- **static_route_payload**: Default route configuration
  - **interfaceName**: Outgoing interface name
  - **selectedNetworks**: Target networks (ID populated with any-ipv4 at runtime)
  - **gateway**: Gateway host object (ID populated at runtime)
  - **metricValue**: Route metric/priority
  - **isTunneled**: VPN tunnel flag
---

## **Usage**

To run the application, execute the following command:

```bash
python src/main_ftd.py
```

### **Workflow**

1. **Displays an ASCII Art Banner**:
   - The script starts by displaying a banner with project details.

2. **Loads Configuration and Credentials**:
   - Reads configuration files and device credentials from JSON files.

3. **Authenticates with EVE-NG**:
   - Logs into the EVE-NG API using the provided credentials.

4. **Deploys FTD Devices**:
   - Creates and starts FTD nodes in EVE-NG using multithreading.

5. **Configures FTD Devices**:
   - Connects to device consoles via VNC and applies initial configuration.

6. **Registers with FMC**:
   - Registers FTD devices with Firepower Management Center.

7. **Configures HA (if applicable)**:
   - Sets up High Availability pairs for FTD devices.

8. **Creates Security Zones**:
   - Creates security zones on the FMC.

9. **Configures Interfaces**:
   - Assigns IP addresses and security zones to physical interfaces.

10. **Sets Up Routing**:
    - Creates host objects and configures default static routes.

---
## **Error Handling**

- **FileNotFoundError**: Raised if a required configuration file is missing.
- **InvalidConfigurationError**: Raised for invalid or malformed configuration files.
- **InvalidDataError**: Raised for missing or invalid data in credential files.
- **RequestException**: Handles API connectivity and HTTP errors.

---

## **Logging**

- **Main Log**: `main_logfile.log` - Captures high-level logs for monitoring application behavior.
- **Real-time Progress**: Progress bars show the status of each automation phase.
- **Queue Messages**: Real-time status updates for each automation task.

---

## **Troubleshooting**

### **API Connectivity**
- **EVE-NG**: Use `troubleshooting/eve_api_connection_test.py` for connectivity testing.
- **FMC**: Use `troubleshooting/fmc_api_connection_test.py` for FMC API testing.

### **Common Issues**
- **VNC Connection**: Ensure EVE-NG VNC ports are accessible.
- **OCR Recognition**: Verify Tesseract is properly installed.
- **API Authentication**: Check credentials and API endpoint URLs.
- **Device Registration**: Verify FTD devices can reach FMC management interface.

---

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## **Maintenance and Updates**

This project is actively maintained to ensure compatibility with the latest versions of EVE-NG, FMC, and Python. Here's how updates and maintenance are handled:

### **Bug Fixes**:
- Known issues are tracked in the GitHub Issues section.
- Fixes are prioritized based on their impact and severity.

### **Feature Updates**:
- New features, such as support for additional FTD configurations or FMC policies, are added periodically.
- Suggestions for new features are welcome! Feel free to open an issue or submit a pull request.

### **Compatibility**:
- The project is tested with the latest versions of Python, EVE-NG, and FMC.
- Dependencies are updated regularly to ensure compatibility and security.

### **Community Contributions**:
- Contributions from the community are encouraged. If you'd like to contribute, please follow the guidelines in the Contributing section.

### **Versioning**:
- The project follows semantic versioning (e.g., v1.0.0).
- Major updates, minor improvements, and patches are documented in the Changelog.

---

## **Contact**

For any questions or support, feel free to reach out:

- **GitHub**: [jotape75](https://github.com/jotape75)
- **Email**: [degraus@gmail.com]
- **LinkedIn**: [https://www.linkedin.com/in/joaopaulocp/]