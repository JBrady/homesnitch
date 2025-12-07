import subprocess
import json
import re
import os
from utils.net_helpers import is_always_listening


def scan_network(subnet="192.168.1.0/24"):
    """Ping-sweep the local network and parse IP, MAC, vendor."""
    devices = []
    try:
        result = subprocess.run(["nmap", "-sn", subnet], capture_output=True, text=True)
        output = result.stdout
        entries = output.split("Nmap scan report for ")[1:]
    except FileNotFoundError:
        # fallback to scapy ARP ping
        try:
            from scapy.all import ARP, Ether, srp
        except ImportError:
            return []
        try:
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0
            )
        except Exception:
            # scapy layer 2 unavailable or other error
            return []
        entries = [
            f"{recv.psrc}\nMAC Address: {recv.hwsrc} (Unknown)" for sent, recv in ans
        ]

    # enrich with type from privacy_scoring (which loads privacy_db.json)
    from backend.privacy_scoring import get_oui_db
    oui_db = get_oui_db()

    for entry in entries:
        lines = entry.strip().splitlines()
        ip = lines[0].strip()
        mac_match = re.search(r"MAC Address: ([0-9A-F:]{17}) \((.*?)\)", entry)
        mac, vendor = (
            (mac_match.group(1), mac_match.group(2))
            if mac_match
            else ("Unknown", "Unknown")
        )
        # lookup prefix (first 3 octets)
        prefix = mac.upper()[0:8]
        profile = oui_db.get(prefix)
        dtype = profile["type"] if profile else "Unknown"
        vendor = profile["vendor"] if profile else vendor
        devices.append(
            {
                "ip": ip,
                "mac": mac,
                "vendor": vendor,
                "type": dtype,
                "always_listening": is_always_listening(vendor),
            }
        )

    return devices


if __name__ == "__main__":
    print(json.dumps(scan_network(), indent=2))
