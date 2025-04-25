from flask import Flask, jsonify, request
from backend.scan import scan_network
from backend.privacy_scoring import score_device
from backend.traffic_monitor import capture_dns_traffic

app = Flask(__name__)

last_report = []

@app.route("/scan")
def scan_endpoint():
    return jsonify(scan_network())


@app.route("/scan_with_score")
def scan_with_score():
    # capture DNS traffic logs for scoring
    traffic_logs = capture_dns_traffic(duration=10)
    devices = scan_network()
    results = [score_device(d, traffic_logs) for d in devices]
    return jsonify(results)


@app.route("/traffic")
def traffic_endpoint():
    """Return raw DNS traffic logs captured for detailed view."""
    logs = capture_dns_traffic(duration=10)
    return jsonify(logs)


@app.route("/report", methods=["POST"])
def report_endpoint():
    data = request.get_json() or {}
    devices = data.get("devices", [])
    dns_logs = data.get("dns_logs", {})
    results = [score_device(d, dns_logs) for d in devices]
    global last_report
    last_report = results
    return jsonify(results)


@app.route("/report", methods=["GET"])
def get_report():
    if not last_report:
        dummy = {
            "ip": "192.168.0.2",
            "mac": "AA:BB:CC:DD:EE:FF",
            "vendor": "Dummy",
            "type": "Test",
            "always_listening": False,
        }
        return jsonify([dummy])
    return jsonify(last_report)


@app.route("/agent/test", methods=["GET"])
def agent_test():
    try:
        # emit and score dummy test device
        dummy = {
            "ip": "192.168.0.99",
            "mac": "AA:BB:CC:DD:EE:FF",
            "vendor": "TestCo",
            "type": "Test",
            "always_listening": False,
        }
        devices = [dummy]
        # use dict entries for scoring function
        dns_logs = {dummy["ip"]: [{"domain": "example.com"}, {"domain": "dummy.test"}]}
        results = [score_device(d, dns_logs) for d in devices]
        global last_report
        last_report = results
        return jsonify({"status": "ok", "devices": devices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
