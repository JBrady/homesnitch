import os

class Config:
    # General Config
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///homesnitch.db")
    # For local Postgres via Docker Compose
    if os.getenv("DATABASE_URI") and os.getenv("DATABASE_URI").startswith("postgres"): 
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "ES256")
    JWT_PRIVATE_KEY = os.getenv("JWT_PRIVATE_KEY")  # PEM-encoded EC private key
    JWT_PUBLIC_KEY = os.getenv("JWT_PUBLIC_KEY")    # PEM-encoded EC public key

    # Load EC keys from backend/keys if env vars not set
    key_dir = os.path.join(os.path.dirname(__file__), "keys")
    priv_path = os.getenv("JWT_PRIVATE_KEY_PATH", os.path.join(key_dir, "ec_private.pem"))
    if not JWT_PRIVATE_KEY and os.path.exists(priv_path):
        with open(priv_path, "r") as f:
            JWT_PRIVATE_KEY = f.read()
    pub_path = os.getenv("JWT_PUBLIC_KEY_PATH", os.path.join(key_dir, "ec_public.pem"))
    if not JWT_PUBLIC_KEY and os.path.exists(pub_path):
        with open(pub_path, "r") as f:
            JWT_PUBLIC_KEY = f.read()

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_CSRF_COOKIE_NAME = "csrf_access_token"
    JWT_REFRESH_CSRF_COOKIE_NAME = "csrf_refresh_token"
