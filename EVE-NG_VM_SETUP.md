# **EVE-NG VM Environment Setup & Troubleshooting**

## **Overview**

This guide addresses common issues when running FTD automation on **EVE-NG Community Edition VMs**. The EVE-NG VM is optimized for networking and lacks GUI automation components needed for headless screenshot capture.

---

## **Problem Identification**

### **Symptoms**
- ❌ **Empty screen captures** (0-byte PNG files)
- ❌ **VNC automation fails** at login detection
- ❌ **OCR returns no text** from FTD console
- ❌ **ModuleNotFoundError** for pyautogui/pyscreeze

### **Root Cause**
EVE-NG VMs are optimized for networking and lack GUI automation components needed for headless screenshot capture.

---

## **Complete EVE-NG VM Fix**

### **1. Install Missing Python Dependencies**
```bash
# Update package manager
sudo apt update

# Install GUI automation packages
pip3 install pyautogui pyscreeze

# Upgrade Pillow to required version
pip3 install --upgrade Pillow

# Install system screenshot tools
sudo apt install -y gnome-screenshot python3-tk scrot xvfb x11-utils
```

### **2. Setup Virtual Display Environment**
```bash
# Create X11 authentication file
touch ~/.Xauthority

# Set display environment variable
export DISPLAY=:99

# Start virtual framebuffer (headless display)
Xvfb :99 -screen 0 1920x1080x24 -ac &
```

### **3. Make Environment Persistent**
```bash
# Add to shell profile for automatic setup
echo "export DISPLAY=:99" >> ~/.bashrc
echo "pgrep Xvfb >/dev/null || Xvfb :99 -screen 0 1920x1080x24 -ac &" >> ~/.bashrc

# Reload profile
source ~/.bashrc
```

### **4. Activate Virtual Environment**
```bash
# Navigate to project and activate venv
cd ~/eve-ng_automation_FTD
source venv/bin/activate
```

### **5. Verification Commands**
```bash
# Verify Python environment
which python
which pip

# Check PyAutoGUI installation
pip list | grep -i pyautogui

# Test PyAutoGUI import and screen detection
python -c "
import pyautogui
print('PyAutoGUI imported successfully')
print(f'Screen size: {pyautogui.size()}')
"

# Test screenshot functionality
python -c "
import pyautogui
import os
pyautogui.screenshot('/tmp/test_capture.png')
size = os.path.getsize('/tmp/test_capture.png')
print(f'Screenshot captured: {size} bytes')
print('✅ Screen capture working!' if size > 0 else '❌ Empty capture file')
"
```

---

## **Expected Results**

### **Before Fix**
```bash
Screenshot Size: 0 bytes (empty captures)
PyAutoGUI: ModuleNotFoundError
Display: echo $DISPLAY returns empty
X11 Auth: Missing .Xauthority file
```

### **After Fix**
```bash
Screenshot Size: 6,108+ bytes (successful capture)
PyAutoGUI: Working in venv (version 0.9.54)
Display: Virtual 1920x1080 resolution (:99)
Screen Capture: pyautogui.screenshot() functional
```

---

**This guide resolves the most common EVE-NG VM compatibility issues for GUI automation and VNC screenshot capture.**