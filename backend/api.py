from flask import Flask, jsonify, request
from backend.scan import scan_network
from backend.privacy_scoring import score_device
from backend.traffic_monitor import capture_dns_traffic
import os
from backend.config import Config
from backend.extensions import db, migrate, jwt, limiter, talisman, cors
from backend.models import User, Report
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
limiter.init_app(app)
cors.init_app(
    app,
    resources={
        r"/*": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"), "supports_credentials": True}
    },
)
# HTTP security headers via Flask-Talisman
talisman.init_app(
    app,
    force_https=not app.debug,
    strict_transport_security=not app.debug,
    content_security_policy={
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "connect-src": ["'self'", os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")],
        "img-src": ["'self'"],
        "style-src": ["'self'", "'unsafe-inline'"],
    },
    frame_options="DENY",
    referrer_policy="no-referrer",
)
if app.debug:
    with app.app_context():
        db.create_all()


@app.route("/scan")
def scan_endpoint():
    return jsonify(scan_network())


@app.route("/scan_with_score")
def scan_with_score():
    try:
        # capture DNS traffic logs for scoring
        traffic_logs = capture_dns_traffic(duration=10)
        devices = scan_network()
        results = [score_device(d, traffic_logs) for d in devices]
        return jsonify(results)
    except Exception as e:
        app.logger.exception("Error in scan_with_score")
        return jsonify({"error": str(e)}), 500


@app.route("/traffic")
def traffic_endpoint():
    """Return raw DNS traffic logs captured for detailed view."""
    logs = capture_dns_traffic(duration=10)
    return jsonify(logs)


@app.route("/report", methods=["POST"])
@jwt_required()
def report_endpoint():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    devices = data.get("devices", [])
    dns_logs = data.get("dns_logs", {})
    report = Report(devices=devices, dns_logs=dns_logs, user_id=user_id)
    db.session.add(report)
    db.session.commit()
    results = [score_device(d, dns_logs) for d in devices]
    return jsonify(results)


@app.route("/report", methods=["GET"])
@jwt_required()
def get_report():
    user_id = get_jwt_identity()
    report = (
        Report.query.filter_by(user_id=user_id)
        .order_by(Report.timestamp.desc())
        .first()
    )
    if not report:
        return jsonify([])
    dns_logs = report.dns_logs
    results = [score_device(d, dns_logs) for d in report.devices]
    return jsonify(results)


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
        # include scored results and remove unused variable warning
        return jsonify({"status": "ok", "devices": devices, "results": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Authentication routes
@app.route("/auth/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User already exists"}), 400
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201


@app.route("/auth/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "Missing email or password"}), 400
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad credentials"}), 401
    # Ensure identity is a string for ES256 subject requirement
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    resp = jsonify({"msg": "Login successful"})
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@app.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    resp = jsonify({"msg": "Token refreshed"})
    set_access_cookies(resp, access_token)
    return resp, 200


@app.route("/auth/logout", methods=["POST"])
def logout():
    resp = jsonify({"msg": "Logged out"})
    unset_jwt_cookies(resp)
    return resp, 200


if __name__ == "__main__":
    # auto-create tables on startup
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
