"""
Basic tests for the Audio Processing Dashboard.
"""
import pytest
from pathlib import Path

from app.config import APP_NAME, UPLOAD_FOLDER


def test_app_name():
    """Test that the app name is set correctly."""
    assert APP_NAME == "Audio Processing Dashboard"


def test_upload_folder_exists():
    """Test that the uploads directory exists."""
    assert UPLOAD_FOLDER.exists()
    assert UPLOAD_FOLDER.is_dir()


# Add more tests as the project develops
