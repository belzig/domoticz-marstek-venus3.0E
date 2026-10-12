#!/usr/bin/python3
import socket
import json
import sys

def set_manual_mode(ip, port=30000):
    payload = {
        "id": 1,
        "method": "ES.SetMode",
        "params": {
            "id": 0,
            "config": {
                "mode": "Manual",
                "manual_cfg": {
                    "time_num": 1,
                    "start_time": "00:00:00",
                    "end_time": "23:59:59",
                    "week_set": 127,
                    "power": 0, # 0 Watt stoppt das Laden
                    "enable": 1
                }
            }
        }
    }
    
    message = json.dumps(payload).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4.0)
    
    try:
        print(f"Sende Manuell-Befehl (0W Limit) an {ip}...")
        sock.sendto(message, (ip, port))
        data, _ = sock.recvfrom(2048)
        print(f"Antwort von Venus erhalten:\n{data.decode('utf-8')}")
    except socket.timeout:
        print("Fehler: Zeitüberschreitung (Timeout).", file=sys.stderr)
    except Exception as e:
        print(f"Fehler: {e}", file=sys.stderr)
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Fehler: Bitte IP-Adresse übergeben. Syntax: python3 venus_set_manual.py <IP>")
        sys.exit(1)
        
    set_manual_mode(sys.argv[1].strip())
