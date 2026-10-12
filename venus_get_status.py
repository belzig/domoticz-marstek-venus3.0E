#!/usr/bin/python3
import socket
import json
import sys

def get_venus_status(ip, port=30000, timeout=3.0):
    payload = {
        "id": 1,
        "method": "ES.GetMode",
        "params": {"id": 0}
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    try:
        sock.sendto(json.dumps(payload).encode('utf-8'), (ip, port))
        data, _ = sock.recvfrom(2048)
        response = json.loads(data.decode('utf-8'))
        result = response.get("result", {})
        
        return {
            "power": result.get("ongrid_power", 0),
            "soc": result.get("bat_soc", result.get("soc", 0))
        }
    except Exception:
        return {"power": 0, "soc": 0}
    finally:
        sock.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Fehler: Bitte IP-Adresse als Argument übergeben.")
        print("Syntax: python3 venus_get_status.py <IP> [power|soc]")
        sys.exit(1)

    target_ip = sys.argv[1].strip()
    status = get_venus_status(target_ip)

    # Wenn ein zweites Argument übergeben wurde (z.B. "soc" oder "power")
    if len(sys.argv) > 2:
        mode = sys.argv[2].lower().strip()
        if mode == "power":
            print(status["power"])
        elif mode == "soc":
            print(status["soc"])
        else:
            print(json.dumps(status))
    else:
        # Standardausgabe als JSON
        print(json.dumps(status))
