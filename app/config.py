"""
Configuration settings for the Audio Processing Dashboard.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

# Application metadata
APP_NAME = "Audio Processing Dashboard"
VERSION = "0.1.0"

# Base directory
BASE_DIR = Path(__file__).parent.parent

# File upload settings
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {
    "wav",
    "mp3",
    "ogg",
    "flac",
    "m4a",
    "wma",
    "aac",
    "WAV",
    "MP3",
    "OGG",
    "FLAC",
    "M4A",
    "WMA",
    "AAC",
}

# Maximum file size for uploads (in bytes)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB


# Default session state
def get_default_session_state():
    """Return default values for the session state."""
    return {
        "uploaded_files": {},
        "active_file": None,
        "active_module": None,
        "module_states": {},
    }


# Default session state for initialization
DEFAULT_SESSION_STATE: Dict[str, Any] = get_default_session_state()

# You can add more configuration settings here as needed
