from backend.privacy_scoring import score_device

def test_score_device_high_risk():
    device = {"ip": "1.2.3.4", "type": "camera", "vendor": "Wyze Labs", "mac": "AA:BB:CC:DD:EE:FF"}
    traffic_logs = {"1.2.3.4": [{"domain": "upload.wyze.com"}]}

    # Camera (+2) + wyze domain (+1) = 3 -> High Risk
    result = score_device(device, traffic_logs)

    assert result["risk_score"] == 3
    assert result["risk_level"] == "High"
    assert "Update Wyze privacy settings" in result["suggestions"]

def test_score_device_medium_risk():
    device = {"ip": "1.2.3.4", "type": "speaker", "vendor": "Unknown", "mac": "AA:BB:CC:DD:EE:FF"}
    traffic_logs = {}

    # Speaker (+2) = 2 -> Medium Risk
    result = score_device(device, traffic_logs)

    assert result["risk_score"] == 2
    assert result["risk_level"] == "Medium"

def test_score_device_low_risk():
    device = {"ip": "1.2.3.4", "type": "fridge", "vendor": "Samsung", "mac": "AA:BB:CC:DD:EE:FF"}
    traffic_logs = {"1.2.3.4": [{"domain": "ntp.org"}]}

    # Fridge (0) + innocent domain (0) = 0 -> Low Risk
    result = score_device(device, traffic_logs)

    assert result["risk_score"] == 0
    assert result["risk_level"] == "Low"

def test_score_device_volume_risk():
    device = {"ip": "1.2.3.4", "type": "generic", "vendor": "Generic", "mac": "AA:BB:CC:DD:EE:FF"}
    # Generate 21 logs
    logs = [{"domain": f"site{i}.com"} for i in range(21)]
    traffic_logs = {"1.2.3.4": logs}

    # Volume > 20 (+2)
    result = score_device(device, traffic_logs)

    assert result["risk_score"] == 2
    assert result["risk_level"] == "Medium"
