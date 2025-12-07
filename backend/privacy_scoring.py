import json
import os

# Load privacy database once at module level
DB_PATH = os.path.join(os.path.dirname(__file__), "privacy_db.json")

def load_privacy_db():
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback empty structure
        return {
            "risk_rules": {"high_risk_types": [], "suspicious_domains": []},
            "suggestions": [],
            "default_suggestion": ["Check vendor privacy guide"],
            "oui_table": {}
        }

PRIVACY_DB = load_privacy_db()

def get_oui_db():
    """Helper to access the OUI table portion of the DB."""
    full_db = PRIVACY_DB
    # Support both old format (direct mapping) and new format (nested under "oui_table")
    if "oui_table" in full_db:
        return full_db["oui_table"]
    return full_db

def get_suggestions(dtype, vendor):
    """Find matching suggestions based on rules."""
    suggestions = []

    # Iterate through rules in the DB
    for rule in PRIVACY_DB.get("suggestions", []):
        criteria = rule.get("criteria", {})

        # Check if rule matches
        match_type = criteria.get("type")
        match_vendor = criteria.get("vendor")

        type_ok = (match_type is None) or (match_type.lower() == dtype)
        vendor_ok = (match_vendor is None) or (match_vendor.lower() == vendor)

        if type_ok and vendor_ok:
            suggestions.extend(rule.get("tips", []))

    if not suggestions:
        return PRIVACY_DB.get("default_suggestion", ["Check vendor privacy guide"])

    # Deduplicate while preserving order
    seen = set()
    return [x for x in suggestions if not (x in seen or seen.add(x))]

def score_device(device, traffic_logs):
    """Data-driven risk assessment."""
    risk = 0
    dtype = device.get("type", "unknown").lower()
    vendor_raw = device.get("vendor", "unknown")
    vendor_lower = vendor_raw.lower()

    rules = PRIVACY_DB.get("risk_rules", {})

    # Check device type risk
    if dtype in rules.get("high_risk_types", []):
        risk += 2

    # Check DNS traffic risk
    suspicious = rules.get("suspicious_domains", [])
    device_logs = traffic_logs.get(device["ip"], [])

    for entry in device_logs:
        domain = entry.get("domain", "")
        if any(susp in domain for susp in suspicious):
            risk += 1

    # weight by DNS query volume
    total_queries = len(device_logs)
    if total_queries > 20:
        risk += 2
    elif total_queries > 5:
        risk += 1

    # collect unique domains for data_sent field
    domains = [entry.get("domain", "") for entry in device_logs]
    data_sent = sorted(set(domains))

    # assign device_id and generate fix suggestions
    device_id = device.get("mac", device.get("ip"))
    suggestions = get_suggestions(dtype, vendor_lower)

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
