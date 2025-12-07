import subprocess
import json
import re
import os
import logging
from flask import current_app
from utils.net_helpers import is_always_listening

logger = logging.getLogger(__name__)

def scan_network(subnet="192.168.1.0/24"):
    """Ping-sweep the local network and parse IP, MAC, vendor."""
    devices = []

    # Try to get Nmap path from config, default to "nmap" if not in app context
    try:
        nmap_path = current_app.config.get("NMAP_PATH", "nmap")
    except RuntimeError:
        nmap_path = "nmap"

    try:
        result = subprocess.run(
            [nmap_path, "-sn", subnet],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        entries = output.split("Nmap scan report for ")[1:]
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.warning(f"Nmap failed or not found ({e}). Falling back to Scapy.")
        # fallback to scapy ARP ping
        try:
            from scapy.all import ARP, Ether, srp
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0
            )
            entries = [
                f"{recv.psrc}\nMAC Address: {recv.hwsrc} (Unknown)" for sent, recv in ans
            ]
        except ImportError:
            logger.error("Scapy not installed. Cannot scan network.")
            return []
        except Exception as e:
            logger.error(f"Scapy scan failed: {e}")
            return []

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
