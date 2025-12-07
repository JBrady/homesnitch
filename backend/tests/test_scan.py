from unittest.mock import patch, MagicMock
from backend.scan import scan_network
import subprocess

def test_scan_endpoint(client):
    # Mock scan_network to return predictable data
    with patch("backend.api.scan_network") as mock_scan:
        mock_scan.return_value = [
            {"ip": "192.168.1.10", "mac": "AA:BB:CC:DD:EE:FF", "vendor": "TestVendor", "type": "TestType", "always_listening": False}
        ]

        response = client.get("/scan")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["ip"] == "192.168.1.10"

def test_scan_with_score_endpoint(client):
    # Mock traffic_monitor and scan_network
    with patch("backend.api.capture_dns_traffic") as mock_capture, \
         patch("backend.api.scan_network") as mock_scan:

        mock_capture.return_value = {"192.168.1.10": [{"domain": "google.com"}]}
        mock_scan.return_value = [
            {"ip": "192.168.1.10", "mac": "AA:BB:CC:DD:EE:FF", "vendor": "Google", "type": "speaker", "always_listening": True}
        ]

        response = client.get("/scan_with_score")
        assert response.status_code == 200
        data = response.get_json()

        assert len(data) == 1
        # Speaker (+2) + google domain (+1) = 3 -> High
        assert data[0]["risk_level"] == "High"

def test_report_creation_and_retrieval(client):
    # Register & Login
    client.post("/auth/register", json={"email": "u@x.com", "password": "p"})
    client.post("/auth/login", json={"email": "u@x.com", "password": "p"})

    # Create Report
    report_data = {
        "devices": [{"ip": "10.0.0.1", "mac": "AA", "vendor": "V", "type": "T"}],
        "dns_logs": {"10.0.0.1": [{"domain": "d.com"}]}
    }
    post_resp = client.post("/report", json=report_data)
    assert post_resp.status_code == 200

    # Get Report
    get_resp = client.get("/report")
    assert get_resp.status_code == 200
    data = get_resp.get_json()
    assert len(data) == 1
    assert data[0]["ip"] == "10.0.0.1"

def test_scan_network_uses_config(app):
    # Test that scan_network uses the configured NMAP_PATH
    with app.app_context():
        app.config["NMAP_PATH"] = "/custom/nmap"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = "Nmap scan report for ..."

            scan_network()

            # Verify subprocess was called with custom path
            args, _ = mock_run.call_args
            assert args[0][0] == "/custom/nmap"

def test_scan_network_nmap_fail_fallback(app):
    with app.app_context():
        # Simulate Nmap failure
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError

            # Mock Scapy fallback
            with patch("scapy.all.srp") as mock_srp:
                # Mock scapy response: list of (sent, recv) tuples
                # recv object needs psrc and hwsrc attributes
                mock_recv = MagicMock()
                mock_recv.psrc = "192.168.1.20"
                mock_recv.hwsrc = "AA:AA:AA:AA:AA:AA"
                mock_srp.return_value = ([(None, mock_recv)], None)

                devices = scan_network()

                assert len(devices) == 1
                assert devices[0]["ip"] == "192.168.1.20"
