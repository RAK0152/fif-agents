"""Model authentication and shared runtime configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def configure() -> str:
    load_dotenv(ROOT / ".env", override=False)
    mode = os.getenv("FIF_AUTH_MODE", "vertex").lower()
    if mode not in {"vertex", "api_key"}:
        raise ValueError("FIF_AUTH_MODE must be vertex or api_key")
    # Explicitly select the backend; API keys must not accidentally override ADC.
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "TRUE" if mode == "vertex" else "FALSE"
    os.environ["GOOGLE_GENAI_USE_ENTERPRISE"] = os.environ["GOOGLE_GENAI_USE_VERTEXAI"]
    if mode == "vertex":
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
    return os.getenv("FIF_MODEL", "gemini-2.5-flash")


def enabled(name: str) -> bool:
    return os.getenv(name, "false").lower() in {"true", "1", "yes"}


def project() -> str:
    value = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    if not value or value == "your-gcp-project-id":
        raise ValueError("Set GOOGLE_CLOUD_PROJECT to your actual project ID")
    return value
