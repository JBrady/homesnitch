import subprocess


def capture_dns_traffic(duration=10):
    """Capture DNS queries for `duration` seconds. Returns dict mapping src IP to list of domains."""
    cmd = [
        "tshark", "-i", "any", "-a", f"duration:{duration}",
        "-Y", "dns.qry.name", "-T", "fields",
        "-e", "ip.src", "-e", "dns.qry.name"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    logs = {}
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        ip, domain = parts
        logs.setdefault(ip, []).append({"domain": domain})
    return logs
