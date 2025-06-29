"""
Utility functions for the Audio Processing Dashboard.
"""

# Import utility functions to make them available at the package level
from .audio_utils import *
from .file_utils import *
from .ui_utils import *

# Re-export specific functions for backward compatibility
from .file_utils import (
    is_audio_file,
    get_file_info,
    create_temp_file,
    copy_file,
    delete_file,
    get_audio_duration,
    get_supported_formats,
    get_supported_mimetypes,
)

from .ui_utils import select_files

from .audio_utils import (
    get_audio_info,
    trim_audio,
    convert_audio,
    normalize_audio,
    extract_audio,
)

__all__ = [
    # File utilities
    "is_audio_file",
    "get_file_info",
    "create_temp_file",
    "copy_file",
    "delete_file",
    "get_audio_duration",
    "get_supported_formats",
    "get_supported_mimetypes",
    # Audio utilities
    "get_audio_info",
    "trim_audio",
    "convert_audio",
    "normalize_audio",
    "extract_audio",
]
