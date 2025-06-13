"""
Volume Control Module

This module provides functionality to adjust the volume of audio files.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import ffmpeg
import streamlit as st

from ..utils import create_temp_file, select_files
from ..utils.audio_utils import get_audio_info
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class VolumeControlModule(BaseModule):
    """Module for adjusting the volume of audio files."""

    config = ModuleConfig(
        name="Volume Control",
        description="Adjust the volume of audio files",
        icon="🔊",
    )

    def __init__(self):
        """Initialize the volume control module."""
        super().__init__()
        self.volume_level = 1.0
        self.normalize = False

    def render_ui(self) -> None:
        """Render the module's user interface."""
        st.header(f"{self.config.icon} {self.config.name}")
        
        # File selection
        selected_files = select_files(
            "Select audio files to adjust volume",
            "volume_control",
            multiple=True,
            file_types=['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        )
        
        if not selected_files:
            return

        # Volume controls
        col1, col2 = st.columns(2)
        
        with col1:
            self.volume_level = st.slider(
                "Volume Level",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="1.0 = original volume, 2.0 = double volume, 0.5 = half volume, up to 10.0"
            )
        
        with col2:
            self.normalize = st.checkbox(
                "Normalize volume across files",
                value=False,
                help="Adjust volume of all files to the same perceived loudness level"
            )
        
        # Process button
        if st.button("Adjust Volume", type="primary"):
            self.process_files(selected_files)
    
    def process(self, input_file: str) -> str:
        """
        Process a single audio file to adjust its volume.
        
        Args:
            input_file: Path to the input audio file
            
        Returns:
            Path to the processed output file
        """
        output_file = create_temp_file(suffix=".wav")
        
        try:
            # Build the FFmpeg command
            stream = ffmpeg.input(input_file)
            
            # Apply volume adjustment
            if self.normalize:
                # Use loudnorm filter for normalization
                stream = stream.filter('loudnorm', i=-23.0, lra=7.0, tp=-2.0, offset=0.0)
            
            # Apply volume scaling
            if self.volume_level != 1.0:
                stream = stream.filter('volume', self.volume_level)
            
            # Output settings
            stream = stream.output(
                output_file,
                ac=2,  # Force stereo output
                ar=44100,  # Standard sample rate
                **{'q:a': 0}  # Best quality VBR
            )
            
            # Run the command
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True, overwrite_output=True)
            
            return output_file
            
        except ffmpeg.Error as e:
            st.error(f"Error processing {Path(input_file).name}: {e.stderr.decode('utf8')}")
            raise

    def process_files(self, files: List[Dict[str, str]]) -> None:
        """
        Process multiple files with progress tracking.
        
        Args:
            files: List of file dictionaries with 'name' and 'path' keys
        """
        if not files:
            return
            
        progress_bar = st.progress(0)
        results = []
        
        for i, file_info in enumerate(files):
            try:
                output_path = self.process(file_info["path"])
                results.append((file_info["name"], output_path, None))
            except Exception as e:
                results.append((file_info["name"], None, str(e)))
            
            # Update progress
            progress = (i + 1) / len(files)
            progress_bar.progress(progress)
        
        # Display results
        self._display_results(results)
    
    def _display_results(self, results: List[tuple]) -> None:
        """
        Display processing results to the user.
        
        Args:
            results: List of tuples (filename, output_path, error)
        """
        st.subheader("Processing Results")
        
        success_count = sum(1 for _, path, error in results if path and not error)
        error_count = len(results) - success_count
        
        if success_count > 0:
            st.success(f"Successfully processed {success_count} file(s)")
        if error_count > 0:
            st.error(f"Failed to process {error_count} file(s)")
        
        # Show download links for successful conversions
        if success_count > 0:
            st.download_button(
                label="Download All Processed Files" if success_count > 1 else "Download Processed File",
                data=b"",  # This is a placeholder - actual download handled by JS
                file_name="volume_adjusted_files.zip",
                mime="application/zip",
                key=f"download_volume_{id(self)}",
                help="Download all processed files as a ZIP archive"
            )
            
            # Add JavaScript to handle the download
            st.markdown(
                f"""
                <script>
                document.querySelector('button[kind="secondary"][title^="Download"]').onclick = function() {{
                    // This will be handled by the file manager's download functionality
                    window.parent.postMessage({{type: 'downloadFiles', files: {json.dumps([r[1] for r in results if r[1]])}}}, '*');
                    return false;
                }};
                </script>
                """,
                unsafe_allow_html=True
            )
