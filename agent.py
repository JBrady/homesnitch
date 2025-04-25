#!/usr/bin/env python3

# Standard library imports
import argparse
import os
import sys
import requests

# ensure backend modules are importable
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Third-party imports
from backend.scan import scan_network
from backend.traffic_monitor import capture_dns_traffic


def main():
    parser = argparse.ArgumentParser(description="HomeSnitch Agent")
    parser.add_argument(
        "--server",
        required=True,
        help="Reporting endpoint URL (e.g. https://api.yoursaas.com/report)",
    )
    parser.add_argument(
        "--subnet", default="192.168.1.0/24", help="Subnet to scan (CIDR)"
    )
    parser.add_argument(
        "--duration", type=int, default=10, help="Seconds to capture DNS traffic"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Emit test devices and logs instead of performing a real scan"
    )
    args = parser.parse_args()

    # test mode: emit dummy data
    if args.test:
        devices = [
            {
                "ip": "192.168.0.99",
                "mac": "AA:BB:CC:DD:EE:FF",
                "vendor": "TestCo",
                "type": "Test",
                "always_listening": False,
            }
        ]
        dns_logs = {"192.168.0.99": ["example.com", "dummy.test"]}
    else:
        devices = scan_network(args.subnet)
        dns_logs = capture_dns_traffic(duration=args.duration)

    payload = {"devices": devices, "dns_logs": dns_logs}

    try:
        resp = requests.post(args.server, json=payload)
        resp.raise_for_status()
        print("Report successful:", resp.json())
    except Exception as e:
        print("Failed to send report:", e)


if __name__ == "__main__":
    main()
