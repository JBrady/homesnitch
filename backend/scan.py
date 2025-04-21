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
            raise RuntimeError(
                "nmap not found and scapy not installed; please install one of them"
            )
        ans, _ = srp(
            Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0
        )
        entries = [
            f"{recv.psrc}\nMAC Address: {recv.hwsrc} (Unknown)" for sent, recv in ans
        ]

    # enrich with type from privacy_db.json (load relative to this file)
    db_path = os.path.join(os.path.dirname(__file__), "privacy_db.json")
    with open(db_path) as f:
        db = json.load(f)

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
        profile = db.get(prefix)
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
