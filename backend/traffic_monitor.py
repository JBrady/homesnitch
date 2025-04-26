import subprocess

try:
    from scapy.all import sniff, DNSQR, IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


def capture_dns_traffic(duration=10):
    """Capture DNS queries for `duration` seconds. Returns dict mapping src IP to list of domains."""
    logs = {}
    if SCAPY_AVAILABLE:
        def process(pkt):
            if pkt.haslayer(DNSQR):
                ip = pkt[IP].src
                domain = pkt[DNSQR].qname.decode().rstrip(".")
                logs.setdefault(ip, []).append({"domain": domain})
        try:
            sniff(filter="udp port 53", timeout=duration, prn=process, store=False)
            return logs
        except Exception:
            # scapy failed, fallback to tshark
            pass

    # fallback to tshark CLI
    cmd = [
        "tshark",
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
        result = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        return {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        ip, domain = parts
        logs.setdefault(ip, []).append({"domain": domain})
    return logs
