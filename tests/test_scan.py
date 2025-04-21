import json
import os
from backend.scan import scan_network


def test_scan_with_nmap(monkeypatch):
    sample_output = """
Nmap scan report for 192.168.1.10
MAC Address: 00:1A:11:22:33:44 (Amazon)
Nmap scan report for 192.168.1.11
MAC Address: D0:73:D5:AA:BB:CC (Wyze Labs)
"""

    class DummyResult:
        stdout = sample_output

    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: DummyResult())
    # write privacy_db.json adjacent to scan.py
    scan_dir = os.path.dirname(__import__("backend.scan").__file__)
    db_path = os.path.join(scan_dir, "privacy_db.json")
    with open(db_path, "w") as f:
        json.dump(
            {
                "00:1A:11": {"vendor": "Amazon", "type": "Speaker"},
                "D0:73:D5": {"vendor": "Wyze Labs", "type": "Camera"},
            },
            f,
        )
    devices = scan_network(subnet="dummy")
    assert devices == [
        {
            "ip": "192.168.1.10",
            "mac": "00:1A:11:22:33:44",
            "vendor": "Amazon",
            "type": "Speaker",
            "always_listening": True,
        },
        {
            "ip": "192.168.1.11",
            "mac": "D0:73:D5:AA:BB:CC",
            "vendor": "Wyze Labs",
            "type": "Camera",
            "always_listening": False,
        },
    ]
