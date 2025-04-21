from flask import Flask, jsonify
from scan import scan_network
from privacy_scoring import score_device
from traffic_monitor import capture_dns_traffic

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
