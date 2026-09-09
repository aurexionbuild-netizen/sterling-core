import socket
import struct
import json
import asyncio
import urllib.request
import sys

# Replace this URL with your actual live Render application URL once deployed!
STERLING_SERVER_URL = "://onrender.com" 

def get_local_ip_range():
    """Dynamically detects the current Wi-Fi/Mesh network subnet range."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually connect, just gets local network routing interface
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()
    
    # Split IP to isolate the network prefix (e.g., 192.168.1.X)
    ip_parts = local_ip.split('.')
    network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
    return network_prefix

async def scan_single_ip(ip, port=80, timeout=0.3):
    """Silently tests if a specific IP address has an active, reachable network node."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return ip
    except:
        return None

async def silent_network_sweep():
    """Performs an incredibly fast, concurrent sweep of all 254 possible network addresses."""
    prefix = get_local_ip_range()
    print(f"[STERLING Client] Initiating silent sweep on roaming subnet: {prefix}0/24")
    
    tasks = []
    for i in range(1, 255):
        target_ip = f"{prefix}{i}"
        tasks.append(scan_single_ip(target_ip))
    
    results = await asyncio.gather(*tasks)
    discovered_ips = [ip for ip in results if ip is not None]
    return discovered_ips

def ship_catalogue_to_tower(devices):
    """Pushes the discovered device registry directly up to the Render Command Tower."""
    url = f"https://{STERLING_SERVER_URL}/ws/network-bridge"
    payload = {
        "type": "NETWORK_CATALOGUE",
        "devices": devices
    }
    
    print(f"[STERLING Client] Encrypting and streaming device registry to Render...")
    # NOTE: In production, we will establish a live WebSocket tunnel here. 
    # For this baseline test, we push the mapping using a secure cloud payload stream.
    try:
        req = urllib.request.Request(
            f"https://{STERLING_SERVER_URL}/api/register-network", 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            print("[STERLING Client] Network bridge synched. Device topology pushed successfully!")
    except Exception as e:
        print(f"[STERLING Client] Synch failed: {e}")

if __name__ == "__main__":
    # Execute the fileless sweep memory cycle
    found_devices = asyncio.run(silent_network_sweep())
    print(f"[STERLING Client] Discovered {len(found_devices)} live endpoints on this network.")
    ship_catalogue_to_tower(found_devices)
