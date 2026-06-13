"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve .env path relative to THIS file → backend/.env
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE)

class Settings:
    """Application settings using simple environment variables."""
    
    # Required keys
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    
    # Optional keys with defaults
    model_name = os.environ.get("MODEL_NAME", "gemini-3.5-flash")
    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    
    # GCP Config
    gcp_project_id = os.environ.get("GCP_PROJECT_ID", "")
    gcp_firestore_database = os.environ.get("GCP_FIRESTORE_DATABASE", "(default)")
    google_application_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "")

settings = Settings()

# CRITICAL WORKAROUND: The antigravity SDK in version 0.1.3 has a bug where
# it fails to recognize the API key when passed via GeminiConfig(api_key=...).
# However, it DOES check os.environ["GEMINI_API_KEY"]. 
# Since we just used load_dotenv, GEMINI_API_KEY is already in os.environ,
# so we don't need to manually set it again.

# Resolve GCP credentials to an absolute path if it is relative
if settings.google_application_credentials and not settings.google_application_credentials.startswith("/"):
    cred_path = Path(__file__).resolve().parent.parent / settings.google_application_credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(cred_path)
