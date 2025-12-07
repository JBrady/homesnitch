import os
from dotenv import load_dotenv
import secrets

# Load .env variables
load_dotenv()


class Config:
    # General Config
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///homesnitch.db")
    # For local Postgres via Docker Compose
    if os.getenv("DATABASE_URI") and os.getenv("DATABASE_URI").startswith("postgres"):
        SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    # Post-Quantum Security: Using HS512 (Symmetric) instead of vulnerable ECDSA
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS512")

    # Generate a strong secret key for JWT signing if not provided
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(64))

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    # allow non-HTTPS cookies in development when FLASK_DEBUG=1
    JWT_COOKIE_SECURE = os.getenv("FLASK_DEBUG", "0") != "1"
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_CSRF_COOKIE_NAME = "csrf_access_token"
    JWT_REFRESH_CSRF_COOKIE_NAME = "csrf_refresh_token"

    # Data-at-rest encryption: switch to SQLCipher driver if key provided
    DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")
    if DB_ENCRYPTION_KEY and SQLALCHEMY_DATABASE_URI.startswith("sqlite:///"):
        # use pysqlcipher3 dialect for encrypted SQLite
        db_path = SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite+pysqlcipher://:{DB_ENCRYPTION_KEY}@/{db_path}"
            "?cipher=aes-256-cbc&kdf_iter=64000"
        )

    # Rate limiter
    RATELIMIT_HEADERS_ENABLED = True

    # CORS settings
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    JWT_COOKIE_CSRF_PROTECT = False  # Simplify testing
