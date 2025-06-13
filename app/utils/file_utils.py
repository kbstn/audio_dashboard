"""
File utility functions for the Audio Processing Dashboard.
"""
import os
import shutil
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
import tempfile
import mimetypes

# Add support for audio MIME types
mimetypes.add_type('audio/wav', '.wav')
mimetypes.add_type('audio/mp3', '.mp3')
mimetypes.add_type('audio/ogg', '.ogg')
mimetypes.add_type('audio/flac', '.flac')
mimetypes.add_type('audio/m4a', '.m4a')
mimetypes.add_type('audio/wma', '.wma')
mimetypes.add_type('audio/aac', '.aac')

def is_audio_file(filepath: str) -> bool:
    """Check if a file is an audio file based on its extension.
    
    Args:
        filepath: Path to the file to check.
        
    Returns:
        bool: True if the file is an audio file, False otherwise.
    """
    # Convert to lowercase and check against known audio extensions
    return Path(filepath).suffix.lower() in [
        '.wav', '.mp3', '.ogg', '.flac', '.m4a', '.wma', '.aac',
        '.WAV', '.MP3', '.OGG', '.FLAC', '.M4A', '.WMA', '.AAC'
    ]

def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get information about an audio file.
    
    Args:
        filepath: Path to the audio file.
        
    Returns:
        dict: Dictionary containing file information.
    """
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    return {
        'name': path.name,
        'path': str(path.absolute()),
        'size': path.stat().st_size,
        'created': path.stat().st_ctime,
        'modified': path.stat().st_mtime,
        'type': mimetypes.guess_type(path)[0] or 'application/octet-stream',
        'is_audio': is_audio_file(path)
    }

def create_temp_file(suffix: str = '.wav') -> str:
    """Create a temporary file with the given suffix.
    
    Args:
        suffix: File extension/suffix for the temporary file.
        
    Returns:
        str: Path to the created temporary file.
    """
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)  # Close the file descriptor as we'll open it later
    return temp_path

def copy_file(src: str, dst: str) -> str:
    """Copy a file from source to destination.
    
    Args:
        src: Source file path.
        dst: Destination directory or file path.
        
    Returns:
        str: Path to the copied file.
    """
    src_path = Path(src)
    dst_path = Path(dst)
    
    # If destination is a directory, append the source filename
    if dst_path.is_dir():
        dst_path = dst_path / src_path.name
    
    # Ensure the destination directory exists
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy the file
    shutil.copy2(src, dst_path)
    return str(dst_path.absolute())

def delete_file(filepath: str) -> None:
    """Delete a file if it exists.
    
    Args:
        filepath: Path to the file to delete.
    """
    path = Path(filepath)
    if path.exists():
        path.unlink()

def get_audio_duration(filepath: str) -> float:
    """Get the duration of an audio file in seconds.
    
    Args:
        filepath: Path to the audio file.
        
    Returns:
        float: Duration in seconds, or 0.0 if duration cannot be determined.
    """
    try:
        # Use pydub to get audio duration
        from pydub import AudioSegment
        audio = AudioSegment.from_file(filepath)
        return len(audio) / 1000.0  # Convert to seconds
    except Exception as e:
        print(f"Error getting audio duration: {e}")
        return 0.0

def get_supported_formats() -> List[str]:
    """Get a list of supported audio file formats.
    
    Returns:
        list: List of supported file extensions.
    """
    return ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.wma', '.aac']

def get_supported_mimetypes() -> List[str]:
    """Get a list of supported audio MIME types.
    
    Returns:
        list: List of supported MIME types.
    """
    return [
        'audio/wav', 'audio/mp3', 'audio/ogg', 'audio/flac',
        'audio/m4a', 'audio/wma', 'audio/aac'
    ]
