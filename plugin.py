#   Marstek Venus E 3.0 Domoticz Python Plugin
#
#   Author: Community
#   License: MIT
#   Requires: Domoticz v2020.2 or higher
#
"""
<plugin key="MarstekVenus" name="Marstek Venus E 3.0 " author="Belzig   " version="1.0.0">
    <description>
        <h2>Marstek Venus E 3.0 UDP Integration</h2>
        Monitors ongrid_power (W) and Battery SoC (%) via local JSON-RPC UDP API.
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="10.55.55.55"/>
        <param field="Port" label="UDP Port" width="100px" required="true" default="30000"/>
        <param field="Mode1" label="Poll Interval (Seconds)" width="100px" required="true" default="30"/>
        <param field="Mode6" label="Debug Log" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import socket
import json

class BasePlugin:
    def __init__(self):
        self.ip = "10.55.55.55"
        self.port = 30000
        self.poll_interval = 61

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            Domoticz.Debug("Debug logging enabled.")

        self.ip = Parameters["Address"]
        self.port = int(Parameters["Port"])
        self.poll_interval = max(10, int(Parameters["Mode1"]))

        Domoticz.Heartbeat(self.poll_interval)

        # 1. Device: VenusPower (Custom Sensor - W)
        if 1 not in Devices:
            Domoticz.Device(
                Name="VenusPower", 
                Unit=1, 
                TypeName="Custom", 
                Options={"Custom": "1;W"},
                Used=1
            ).Create()
            Domoticz.Log("Created device 'VenusPower' (Unit 1).")

        # 2. Device: VenusSOC (Custom Sensor - %)
        if 2 not in Devices:
            Domoticz.Device(
                Name="VenusSOC", 
                Unit=2, 
                TypeName="Custom", 
                Options={"Custom": "1;%"},
                Used=1
            ).Create()
            Domoticz.Log("Created device 'VenusSOC' (Unit 2).")

        Domoticz.Log(f"Marstek Venus Plugin started for {self.ip}:{self.port} (Poll: {self.poll_interval}s)")

    def onStop(self):
        Domoticz.Log("Marstek Venus Plugin stopped.")

    def onHeartbeat(self):
        payload = {
            "id": 1,
            "method": "ES.GetMode",
            "params": {"id": 0}
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)

        try:
            sock.sendto(json.dumps(payload).encode('utf-8'), (self.ip, self.port))
            data, _ = sock.recvfrom(2048)
            
            try:
                response = json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                Domoticz.Error("Failed to decode JSON response from Marstek device.")
                return

            result = response.get("result", {})
            
            # Extract values with fallbacks for different firmware versions
            ongrid_power = result.get("ongrid_power", None)
            soc = result.get("bat_soc", result.get("soc", None))

            # Update Power
            if ongrid_power is not None:
                Devices[1].Update(nValue=0, sValue=str(ongrid_power))
                Domoticz.Debug(f"Updated VenusPower: {ongrid_power} W")

            # Update SoC
            if soc is not None:
                Devices[2].Update(nValue=0, sValue=str(soc))
                Domoticz.Debug(f"Updated VenusSOC: {soc} %")

        except socket.timeout:
            Domoticz.Error(f"Timeout during UDP request to Marstek Venus ({self.ip}:{self.port})")
        except Exception as e:
            Domoticz.Error(f"Error communicating with Marstek Venus: {str(e)}")
        finally:
            sock.close()

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onConnect(Status, Description): pass
def onMessage(Data): pass
def onCommand(Unit, Command, Level, Hue): pass
def onNotification(Data): pass
def onDisconnect(): pass
