import subprocess
import logging
from flask import current_app

logger = logging.getLogger(__name__)

try:
    from scapy.all import sniff, DNSQR, IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


def capture_dns_traffic(duration=10):
    """Capture DNS queries for `duration` seconds. Returns dict mapping src IP to list of domains."""
    logs = {}

    # Try to get paths from config
    try:
        tshark_path = current_app.config.get("TSHARK_PATH", "tshark")
    except RuntimeError:
        tshark_path = "tshark"

    if SCAPY_AVAILABLE:
        def process(pkt):
            if pkt.haslayer(DNSQR):
                try:
                    if IP in pkt:
                        ip = pkt[IP].src
                        domain = pkt[DNSQR].qname.decode().rstrip(".")
                        logs.setdefault(ip, []).append({"domain": domain})
                except Exception as e:
                    logger.debug(f"Error processing packet: {e}")

        try:
            sniff(filter="udp port 53", timeout=duration, prn=process, store=False)
            return logs
        except Exception as e:
            logger.warning(f"Scapy sniff failed ({e}). Fallback to tshark.")
            # scapy failed, fallback to tshark
            pass

    # fallback to tshark CLI
    cmd = [
        tshark_path,
        "-i",
        "any",
        "-a",
        f"duration:{duration}",
        "-Y",
        "dns.qry.name",
        "-T",
        "fields",
        "-e",
        "ip.src",
        "-e",
        "dns.qry.name"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.error(f"Tshark failed or not found ({e}). Traffic monitoring failed.")
        return {}

    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        ip, domain = parts
        logs.setdefault(ip, []).append({"domain": domain})
    return logs
