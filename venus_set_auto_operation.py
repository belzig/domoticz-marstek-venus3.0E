#!/usr/bin/python3
import socket
import json
import sys
import time

def set_auto_mode(ip, port=30000):
    payload = {
        "id": 1,
        "method": "ES.SetMode",
        "params": {
            "id": 0,
            "config": {
                "mode": "Auto",
                "auto_cfg": {
                    "enable": 1
                }
            }
        }
    }
    
    message = json.dumps(payload).encode('utf-8')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(4.0)
    
    try:
        # API-Workaround: Doppeltes Senden wegen Puffer-Trägheit der Venus E 3.0
        for i in range(2):
            print(f"Sende Eigenbedarf-Befehl an {ip} (Versuch {i+1})...")
            sock.sendto(message, (ip, port))
            time.sleep(0.3)
        
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
        print("Fehler: Bitte IP-Adresse übergeben. Syntax: python3 venus_set_auto.py <IP>")
        sys.exit(1)
        
    set_auto_mode(sys.argv[1].strip())
