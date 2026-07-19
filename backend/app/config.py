import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
ENV_FILE = BASE_DIR.parent / ".env"

DEMO_USERNAME = "user"
DEMO_PASSWORD = "password"


def get_session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-secret-change-me")
