import os
import sys

# ensure project root in sys.path for backend imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Wire env vars for JWT keys
os.environ["JWT_PRIVATE_KEY"] = open("backend/keys/ec_private.pem").read()
os.environ["JWT_PUBLIC_KEY"] = open("backend/keys/ec_public.pem").read()
# Ensure frontend origin and Flask app
os.environ["FLASK_APP"] = "backend.api"
os.environ["FRONTEND_ORIGIN"] = "http://localhost:3000"

# Import app after env vars loaded
from backend.api import app

if __name__ == "__main__":
    client = app.test_client()

    # Test registration
    r1 = client.post(
        "/auth/register", json={"email": "test@example.com", "password": "secret"}
    )
    print("Register:", r1.status_code, r1.get_json())

    # Test login
    r2 = client.post(
        "/auth/login", json={"email": "test@example.com", "password": "secret"}
    )
    print("Login:", r2.status_code, r2.get_json())
    # Show cookies set
    print("Set-Cookie headers:", r2.headers.getlist("Set-Cookie"))
