import subprocess
import json
import re
import os
import logging
import xml.etree.ElementTree as ET
from flask import current_app
from utils.net_helpers import is_always_listening

logger = logging.getLogger(__name__)

def scan_network(subnet="192.168.1.0/24"):
    """Ping-sweep the local network and parse IP, MAC, vendor."""
    devices = []

    # enrich with type from privacy_scoring (which loads privacy_db.json)
    from backend.privacy_scoring import get_oui_db
    oui_db = get_oui_db()

    # Try to get Nmap path from config, default to "nmap" if not in app context
    try:
        nmap_path = current_app.config.get("NMAP_PATH", "nmap")
    except RuntimeError:
        nmap_path = "nmap"

    try:
        result = subprocess.run(
            [nmap_path, "-sn", subnet, "-oX", "-"],
            capture_output=True,
            text=True,
            check=True
        )

        root = ET.fromstring(result.stdout)
        for host in root.findall("host"):
            ip = "Unknown"
            mac = "Unknown"
            vendor = "Unknown"

            for addr in host.findall("address"):
                addr_type = addr.get("addrtype")
                if addr_type == "ipv4":
                    ip = addr.get("addr")
                elif addr_type == "mac":
                    mac = addr.get("addr")
                    vendor = addr.get("vendor", "Unknown")

            # Only add if we found an IP (MAC might be missing for localhost, but usually present for LAN scan)
            if ip != "Unknown":
                # enrich
                # Normalize MAC to UPPER case just in case
                mac = mac.upper() if mac else "Unknown"
                prefix = mac[0:8] if mac != "Unknown" else ""
                profile = oui_db.get(prefix)
                dtype = profile["type"] if profile else "Unknown"
                vendor = profile["vendor"] if profile else vendor

                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor,
                    "type": dtype,
                    "always_listening": is_always_listening(vendor),
                })
        return devices

    except (FileNotFoundError, subprocess.CalledProcessError, ET.ParseError) as e:
        logger.warning(f"Nmap failed or not found ({e}). Falling back to Scapy.")
        # fallback to scapy ARP ping
        try:
            from scapy.all import ARP, Ether, srp
            ans, _ = srp(
                Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0
            )
            for sent, recv in ans:
                ip = recv.psrc
                mac = recv.hwsrc.upper()
                vendor = "Unknown"

                # enrich
                prefix = mac[0:8]
                profile = oui_db.get(prefix)
                dtype = profile["type"] if profile else "Unknown"
                vendor = profile["vendor"] if profile else vendor

                devices.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor,
                    "type": dtype,
                    "always_listening": is_always_listening(vendor),
                })
            return devices

        except ImportError:
            logger.error("Scapy not installed. Cannot scan network.")
            return []
        except Exception as e:
            logger.error(f"Scapy scan failed: {e}")
            return []

if __name__ == "__main__":
    print(json.dumps(scan_network(), indent=2))
