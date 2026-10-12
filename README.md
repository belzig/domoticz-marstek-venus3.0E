# Domoticz Marstek Venus E 3.0 Integration

A local, cloud-free integration for the **Marstek Venus E 3.0 (Firmware v3.0+)** energy storage system via its local JSON-RPC UDP API. This repository provides a Domoticz Python Plugin for continuous monitoring and a set of robust standalone Python scripts to control charging behavior without crashing the unstable Venus API.

---

## ⚠️ The Problem with the Venus API

The Marstek Venus E 3.0 local API is notoriously prone to buffer overflows and crashes if it receives too many commands or rapid polling. When it crashes, it often drops all user settings and resets to factory defaults. 

**This integration solves this issue using two strategies:**
1. **Low Frequency Polling:** The Domoticz plugin is hardcoded to a safe 61-second heartbeat interval to prevent flooding the API.
2. **Stateless Standalone Control:** Changing modes (e.g., stopping the charge at 80%) is **not** handled inside the continuous plugin. Instead, simple, standalone scripts send **one single UDP packet** and exit instantly. This keeps the Venus buffer clear and perfectly stable.

---

## 📦 Features

- **`plugin.py`**: A Domoticz Python Plugin that safely reads current Grid Power (W) and Battery State of Charge (SoC %).
- **`venus_get_status.py`**: A fast script to request SoC and Grid Power. Returns a clean JSON string or specific values via arguments.
- **`venus_set_manual.py`**: Sets the Venus E to manual mode with a time frame of 00:00-23:59 and **0 Watts target power**. This safely halts the charging process at your desired threshold (e.g., 80% SoC) to protect your LiFePO4 cells.
- **`venus_set_auto.py`**: Releases the manual lock and returns the Venus E back to its default "Auto" (SelfUse / Eigenbedarf) mode using the strict nested parameters (`auto_cfg`) required by the v3.0 firmware.

---

## 🚀 How to Install / Download

Log into your Domoticz server (e.g., Raspberry Pi) via SSH and follow these steps to clone and install the files:

### 1. Clone the Repository
Navigate to your Domoticz plugins directory and clone this project:
```bash
cd /home/pi/domoticz/plugins/
git clone https://github.com/belzig/domoticz-marstek-venus3.0E MarstekVenus
```

### 2. Copy and Set Up the Standalone Scripts
The Python control scripts need to be located in the central Domoticz scripts directory. You can use the included shell script to copy them into the correct folder and set the execution flags automatically:
```bash
cd /home/pi/domoticz/plugins/MarstekVenus/
chmod +x copy_venus_scripts.sh
./copy_venus_scripts.sh
```

## 🛠️ File System Structure

For Domoticz to execute these scripts securely, please arrange them as follows on your Domoticz system:

```text
home/
└── pi/
    └── domoticz/
        ├── plugins/
        │   └── MarstekVenus/
        │       └── plugin.py               <-- Main Domoticz Plugin
        └── scripts/
          ├── venus_get_status.py     <-- Read Status
          ├── venus_set_manual.py     <-- Stop Charge (0W)
          └── venus_set_auto.py       <-- Resume Auto Mode
```

### Making the standalone scripts executable
Log into your Domoticz server via SSH and grant execution permissions to the Python scripts:
```bash
chmod +x /home/pi/domoticz/scripts/venus_set_*.py
chmod +x /home/pi/domoticz/scripts/venus_get_status.py
```

---

## ⚙️ Domoticz Configuration

### 1. Hardware Setup (Plugin)
1. Go to **Setup -> Hardware** in Domoticz.
2. Add a new hardware entry of type **Marstek Venus E 3.0**.
3. Set your Venus E IP Address and keep the default port `30000`.
4. Keep the Poll Interval set to **61 seconds** to maintain stability.
5. Click **Add**. This automatically creates two devices: `VenusPower` (W) and `VenusSOC` (%).

### 2. Manual/Auto Virtual Tasters (Push Buttons)
To safely switch modes, create two Virtual Push Buttons in Domoticz to trigger the Python scripts.

1. Go to **Setup -> Hardware** and click **Create Virtual Sensors** on your *Dummy* hardware.
2. Create two switches: name them `Venus_Set_Manual` and `Venus_Set_Auto`.
3. Go to the **Switches** tab, click **Edit** on each button and change the **Switch Type** to **Push On Button**.
4. In the **On Action** field, enter the following system paths (replace `10.55.55.55` with your actual Venus IP):

- **`Venus_Set_Manual` On-Action:**
  ```text
  script://venus_set_manual.py 10.55.55.55
  ```
- **`Venus_Set_Auto` On-Action:**
  ```text
  script://venus_set_auto.py 10.55.55.55
  ```

---

## 🤖 Automating the 80% SoC Limit (dzVents)

Now you can create a simple `dzVents` script inside Domoticz (**Setup -> More Options -> Events**) to automate the battery protection logic. This logic activates manual mode at 80% and resumes auto mode once the battery discharges back to 78%:

```lua
return {
    on = {
        devices = {
            'VenusSOC' -- The name of your Venus SoC device created by the plugin
        }
    },
    execute = function(domoticz, device)
        -- Stop charging when battery hits 80%
        if (device.value >= 80) then
            domoticz.log('Venus SoC reached 80%. Activating 0W Manual Limit.', domoticz.LOG_INFO)
            domoticz.devices('Venus_Set_Manual').switchOn().checkFirst()
        
        -- Return to Auto Mode once battery drops below 78%
        elseif (device.value <= 78) then
            domoticz.log('Venus SoC dropped below 78%. Releasing limit to Auto Mode.', domoticz.LOG_INFO)
            domoticz.devices('Venus_Set_Auto').switchOn().checkFirst()
        end
    end
end
```

*Note: Since LiFePO4 cells need occasional cell-balancing at 100% to keep the BMS percentage accurate, it is recommended to bypass this automation once every 2-4 weeks to allow a full 100% charge cycle.*

---

## 📝 License
This project is licensed under the MIT License - feel free to use and adapt it for your home automation!
