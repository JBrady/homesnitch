def score_device(device, traffic_logs):
    """Simple heuristic to assign risk levels."""
    risk = 0
    dtype = device.get("type", "unknown").lower()
    vendor_raw = device.get("vendor", "unknown")
    vendor_lower = vendor_raw.lower()

    if dtype in ("camera", "microphone", "speaker"):
        risk += 2

    for entry in traffic_logs.get(device["ip"], []):
        domain = entry.get("domain", "")
        if any(dom in domain for dom in ("amazon", "roku", "wyze", "nest", "google")):
            risk += 1

    # weight by DNS query volume
    total_queries = len(traffic_logs.get(device["ip"], []))
    if total_queries > 20:
        risk += 2
    elif total_queries > 5:
        risk += 1

    # collect unique domains for data_sent field
    domains = [entry.get("domain", "") for entry in traffic_logs.get(device["ip"], [])]
    data_sent = sorted(set(domains))

    # assign device_id and generate fix suggestions
    device_id = device.get("mac", device.get("ip"))
    suggestions = []
    if dtype == "speaker" and vendor_lower == "amazon":
        suggestions = [
            "Mute mic when not in use",
            "Block metrics.amazon.com",
            "Review Alexa Privacy Settings",
        ]
    elif dtype == "camera" and vendor_lower == "wyze labs":
        suggestions = [
            "Block upload.wyze.com in firewall",
            "Update Wyze privacy settings",
        ]
    elif dtype == "smart tv" or vendor_lower == "roku":
        suggestions = [
            "Review Roku privacy settings",
            "Block logs.rkuservice.net",
        ]
    else:
        suggestions = ["Check vendor privacy guide"]

    level = "High" if risk >= 3 else "Medium" if risk == 2 else "Low"
    return {
        "id": device_id,
        "ip": device["ip"],
        "vendor": vendor_raw,
        "type": device.get("type"),
        "risk_score": risk,
        "risk_level": level,
        "query_count": total_queries,
        "data_sent": data_sent,
        "suggestions": suggestions,
    }
