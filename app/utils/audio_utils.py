"""
Audio processing utilities for the Audio Processing Dashboard.
"""
import os
import tempfile
import numpy as np
import ffmpeg
from pathlib import Path
from typing import Optional, Tuple, Union, List, Dict, Any

# Import file utilities
from .file_utils import create_temp_file, delete_file


def get_audio_info(filepath: str) -> Dict[str, Any]:
    """Get detailed information about an audio file using ffprobe.

    Args:
        filepath: Path to the audio file.

    Returns:
        dict: Dictionary containing audio file information.
    """
    try:
        probe = ffmpeg.probe(filepath)
        audio_info = next(s for s in probe["streams"] if s["codec_type"] == "audio")

        return {
            "duration": float(audio_info.get("duration", 0)),
            "sample_rate": int(audio_info.get("sample_rate", 44100)),
            "channels": int(audio_info.get("channels", 2)),
            "codec": audio_info.get("codec_name", "unknown"),
            "bitrate": int(audio_info.get("bit_rate", 0))
            if "bit_rate" in audio_info
            else 0,
            "format": probe.get("format", {}).get("format_name", "unknown"),
            "size": int(probe.get("format", {}).get("size", 0)),
        }
    except ffmpeg.Error as e:
        print(f"Error getting audio info: {e.stderr.decode()}")
        return {}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {}


def trim_audio(
    input_file: str,
    output_file: Optional[str] = None,
    start_time: float = 0.0,
    end_time: Optional[float] = None,
    format: str = None,
) -> str:
    """Trim an audio file using ffmpeg.

    Args:
        input_file: Path to the input audio file.
        output_file: Path to save the trimmed audio file. If None, a temp file is created.
        start_time: Start time in seconds.
        end_time: End time in seconds. If None, trims to the end of the file.
        format: Output format/extension. If None, uses the same as input.

    Returns:
        str: Path to the trimmed audio file.
    """
    try:
        # Get input file info
        input_info = get_audio_info(input_file)
        if not input_info:
            raise ValueError("Could not read input file information")

        # Use input file's format if none specified
        if format is None:
            format = Path(input_file).suffix.lstrip(".")
            if not format:  # If no extension, default to wav
                format = "wav"

        # Create output file if not provided
        if output_file is None:
            output_file = create_temp_file(suffix=f".{format}")

        # Build the ffmpeg command
        stream = ffmpeg.input(input_file, ss=start_time)

        # Add end time if specified
        if end_time is not None:
            stream = ffmpeg.filter(stream, "atrim", end=end_time - start_time)

        # Set output options based on format
        output_kwargs = {
            "loglevel": "error",  # Only show errors
            "y": None,  # Overwrite output file if it exists
        }

        # For WAV output, use pcm_s16le codec
        if format.lower() == "wav":
            output_kwargs.update(
                {
                    "acodec": "pcm_s16le",
                    "ar": input_info.get("sample_rate", 44100),
                    "ac": input_info.get("channels", 2),
                }
            )
        # For MP3 output, use libmp3lame with reasonable quality
        elif format.lower() == "mp3":
            output_kwargs.update(
                {"acodec": "libmp3lame", "q:a": 2}  # VBR quality, 0-9 where 0 is best
            )
        # For other formats, let ffmpeg choose the best codec

        # Create output stream
        stream = ffmpeg.output(stream, output_file, **output_kwargs)

        # Run the command
        ffmpeg.run(
            stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
        )

        return output_file

    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        print(f"FFmpeg error: {error_message}")
        if output_file and os.path.exists(output_file):
            delete_file(output_file)
        raise Exception(f"Error trimming audio: {error_message}")
    except Exception as e:
        if "output_file" in locals() and output_file and os.path.exists(output_file):
            delete_file(output_file)
        raise Exception(f"Error processing audio: {str(e)}")


def convert_audio(
    input_file: str,
    output_file: Optional[str] = None,
    format: str = "mp3",
    bitrate: str = "192k",
    sample_rate: int = 44100,
    channels: int = 2,
) -> str:
    """Convert an audio file to a different format.

    Supported formats:
    - MP3: Uses libmp3lame codec
    - WAV: Uses pcm_s16le codec (uncompressed)
    - FLAC: Uses flac codec (lossless)
    - OGG: Uses libvorbis codec
    - M4A/AAC: Uses aac codec
    
    Args:
        input_file: Path to the input audio file.
        output_file: Path to save the converted audio file. If None, a temp file is created.
        format: Output format/extension (mp3, wav, flac, ogg, m4a, aac).
        bitrate: Output bitrate (e.g., '128k', '192k', '320k').
        sample_rate: Output sample rate in Hz.
        channels: Number of output channels.

    Returns:
        str: Path to the converted audio file.
    """
    if output_file is None:
        output_file = create_temp_file(f".{format}")

    # Normalize format string (remove dot if present and convert to lowercase)
    format = format.lower().lstrip('.')
    
    # Map formats to their respective codecs and options
    format_codecs = {
        'mp3': 'libmp3lame',
        'wav': 'pcm_s16le',  # Uncompressed WAV
        'flac': 'flac',      # Lossless
        'ogg': 'libvorbis',  # Ogg Vorbis
        'm4a': 'aac',        # AAC in M4A container
        'aac': 'aac'         # Raw AAC
    }
    
    # Default output extension if not provided
    output_ext = f".{format}"
    
    # Special handling for formats that need specific containers
    if format == 'm4a':
        output_ext = '.m4a'  # Force .m4a extension for AAC in MP4 container
    elif format == 'aac':
        output_ext = '.aac'  # Raw AAC
    
    if output_file is None:
        output_file = create_temp_file(output_ext)
    
    # Ensure output file has correct extension
    output_path = Path(output_file)
    if output_path.suffix.lower() != output_ext:
        output_file = str(output_path.with_suffix(output_ext))

    try:
        stream = ffmpeg.input(input_file)
        
        # Get the appropriate codec for the output format
        codec = format_codecs.get(format)
        
        # Build output options
        output_kwargs = {
            'ar': sample_rate,
            'ac': channels,
            'loglevel': 'error',
            'y': None,  # Overwrite output file if it exists
        }
        
        # Set codec if specified
        if codec:
            output_kwargs['acodec'] = codec
            
        # Special handling for different formats
        if format == 'wav':
            # WAV is uncompressed, doesn't use bitrate
            output_kwargs['ar'] = sample_rate
            output_kwargs['ac'] = channels
        elif format == 'flac':
            # FLAC is lossless, uses compression level instead of bitrate
            output_kwargs['compression_level'] = 8  # 0 (fastest) to 8 (best compression)
        else:
            # For other formats, set the bitrate
            output_kwargs['audio_bitrate'] = bitrate
        
        # Special handling for M4A/AAC
        if format in ['m4a', 'aac']:
            output_kwargs['strict'] = 'experimental'  # Sometimes needed for AAC
            if format == 'm4a':
                output_kwargs['f'] = 'ipod'  # Use iPod-compatible format for M4A
        
        # Create output stream
        stream = ffmpeg.output(stream, output_file, **output_kwargs)

        # Run the command
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return output_file
        
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if e.stderr else str(e)
        print(f"Error converting audio: {error_msg}")
        if os.path.exists(output_file):
            delete_file(output_file)  # Clean up the output file on error
        raise Exception(f"FFmpeg error: {error_msg}")
    except Exception as e:
        if 'output_file' in locals() and os.path.exists(output_file):
            delete_file(output_file)
        raise Exception(f"Error converting audio: {str(e)}")


def normalize_audio(
    input_file: str, output_file: Optional[str] = None, target_level: float = -1.0
) -> str:
    """Normalize the audio to a target level.

    Args:
        input_file: Path to the input audio file.
        output_file: Path to save the normalized audio file. If None, a temp file is created.
        target_level: Target level in dBFS (e.g., -1.0 for -1 dBFS).

    Returns:
        str: Path to the normalized audio file.
    """
    if output_file is None:
        output_file = create_temp_file(".wav")

    try:
        stream = ffmpeg.input(input_file)

        # Apply normalization
        stream = ffmpeg.filter(stream, "loudnorm", I=target_level)

        # Set output options
        stream = ffmpeg.output(
            stream,
            output_file,
            acodec="pcm_s16le",
            ar=44100,
            ac=2,
            loglevel="error",  # Only show errors
        )

        # Run the command
        ffmpeg.run(
            stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
        )

        return output_file
    except ffmpeg.Error as e:
        delete_file(output_file)  # Clean up the output file on error
        print(f"Error normalizing audio: {e.stderr.decode()}")
        raise


def extract_audio(
    input_file: str, output_file: Optional[str] = None, format: str = "wav"
) -> str:
    """Extract audio from a video or audio file.

    Args:
        input_file: Path to the input file (video or audio).
        output_file: Path to save the extracted audio file. If None, a temp file is created.
        format: Output format/extension.

    Returns:
        str: Path to the extracted audio file.
    """
    if output_file is None:
        output_file = create_temp_file(f".{format}")

    try:
        stream = ffmpeg.input(input_file)

        # Extract audio stream
        stream = stream.audio

        # Set output options
        stream = ffmpeg.output(
            stream,
            output_file,
            acodec="pcm_s16le" if format == "wav" else None,
            ar=44100,
            ac=2,
            loglevel="error",  # Only show errors
        )

        # Run the command
        ffmpeg.run(
            stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
        )

        return output_file
    except ffmpeg.Error as e:
        delete_file(output_file)  # Clean up the output file on error
        print(f"Error extracting audio: {e.stderr.decode()}")
        raise


def merge_audio(
    input_files: List[str],
    output_file: Optional[str] = None,
    output_format: str = "mp3",
) -> str:
    """Merge multiple audio files into a single file.

    Args:
        input_files: List of paths to input audio files.
        output_file: Path to save the merged audio file. If None, a temp file is created.
        output_format: Output format/extension (default: mp3).

    Returns:
        str: Path to the merged audio file.
    """
    if not input_files:
        raise ValueError("No input files provided")

    if len(input_files) == 1:
        # If only one file, just return it
        return input_files[0]

    if output_file is None:
        output_file = create_temp_file(f".{output_format}")

    try:
        # Create a list of input streams
        streams = [ffmpeg.input(f) for f in input_files]
        
        # Concatenate the audio streams
        merged = ffmpeg.concat(*streams, v=0, a=1)
        
        # Set output options
        output_kwargs = {
            "loglevel": "error",
            "y": None,  # Overwrite output file if it exists
        }

        # For WAV output, use pcm_s16le codec
        if output_format.lower() == "wav":
            output_kwargs.update({
                "acodec": "pcm_s16le",
                "ar": 44100,
                "ac": 2,
            })
        # For MP3 output, use libmp3lame with reasonable quality
        elif output_format.lower() == "mp3":
            output_kwargs.update({"acodec": "libmp3lame", "q:a": 2})

        # Create output stream
        stream = ffmpeg.output(merged, output_file, **output_kwargs)

        # Run the command
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return output_file

    except ffmpeg.Error as e:
        if output_file and os.path.exists(output_file):
            delete_file(output_file)
        print(f"Error merging audio: {e.stderr.decode() if e.stderr else str(e)}")
        raise Exception(f"Error merging audio: {e.stderr.decode() if e.stderr else str(e)}")
    except Exception as e:
        if 'output_file' in locals() and output_file and os.path.exists(output_file):
            delete_file(output_file)
        print(f"Unexpected error merging audio: {str(e)}")
        raise Exception(f"Error processing audio: {str(e)}")
