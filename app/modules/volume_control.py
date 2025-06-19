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
from pydantic import BaseModel, Field

from ..utils import create_temp_file, select_files
from ..utils.audio_utils import get_audio_info
from ..session_state import add_uploaded_file
from .base_module import BaseModule, ModuleConfig, register_module


class VolumeSettings(BaseModel):
    """Settings for the Volume Control module."""
    
    volume_level: float = Field(1.0, ge=0.1, le=10.0, description="Volume level (1.0 = original)")
    normalize: bool = Field(False, description="Normalize volume across files")
    output_prefix: str = Field("vol_", description="Prefix for output filenames")


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
        self.settings = VolumeSettings()
        self.audio_info: Dict[str, Any] = {}
        self.output_file: Optional[str] = None

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

        # Show audio info if a single file is selected
        if len(selected_files) == 1:
            try:
                file_path = selected_files[0]["path"]
                self.audio_info = get_audio_info(file_path)
                
                # Display audio information
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Duration", f"{self.audio_info.get('duration', 0):.2f} s")
                with col2:
                    st.metric("Sample Rate", f"{self.audio_info.get('sample_rate', 0)} Hz")
                with col3:
                    st.metric("Channels", self.audio_info.get('channels', 0))
            except Exception as e:
                st.warning(f"Could not read audio info: {str(e)}")
        
        # Volume controls
        with st.expander("Volume Settings", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                self.settings.volume_level = st.slider(
                    "Volume Level",
                    min_value=0.1,
                    max_value=10.0,
                    value=self.settings.volume_level,
                    step=0.1,
                    help="1.0 = original volume, 2.0 = double volume, 0.5 = half volume, up to 10.0"
                )
            
            with col2:
                self.settings.normalize = st.checkbox(
                    "Normalize volume across files",
                    value=self.settings.normalize,
                    help="Adjust volume of all files to the same perceived loudness level"
                )
            
            # Output settings
            self.settings.output_prefix = st.text_input(
                "Output filename prefix",
                value=self.settings.output_prefix,
                help="Prefix to add to processed filenames"
            )
        
        # Process button
        if st.button("Adjust Volume", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                self.process_files(selected_files)
    
    def process(self, input_file: str) -> str:
        """
        Process a single audio file to adjust its volume.
        
        Args:
            input_file: Path to the input audio file
            
        Returns:
            Path to the processed output file
        """
        try:
            # Create a temporary file with the same extension as input
            input_path = Path(input_file)
            output_file = create_temp_file(suffix=input_path.suffix)
            
            # Build the FFmpeg command
            stream = ffmpeg.input(input_file)
            
            # Apply volume adjustment
            if self.settings.normalize:
                # Use loudnorm filter for normalization
                stream = stream.filter('loudnorm', i=-23.0, lra=7.0, tp=-2.0, offset=0.0)
            
            # Apply volume scaling
            if self.settings.volume_level != 1.0:
                stream = stream.filter('volume', self.settings.volume_level)
            
            # Output settings - preserve original format and metadata
            output_args = {
                'q:a': '0',  # Best quality VBR
                'y': None,   # Overwrite output file if it exists
                'loglevel': 'warning'  # Reduce log verbosity
            }
            
            # Preserve metadata if possible
            if input_path.suffix.lower() in ['.mp3', '.m4a', '.aac']:
                output_args['map_metadata'] = '0'
            
            stream = stream.output(str(output_file), **output_args)
            
            # Run the command
            ffmpeg.run(stream, overwrite_output=True)
            
            return str(output_file)
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf8') if e.stderr else str(e)
            st.error(f"Error processing {Path(input_file).name}: {error_msg}")
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
                if output_path:
                    # Get the output filename with prefix
                    output_filename = f"{self.settings.output_prefix}{Path(file_info['name']).name}"
                    
                    # Create a new path with the desired filename in the same directory
                    output_dir = Path(output_path).parent
                    final_output_path = output_dir / output_filename
                    
                    # Rename the temp file to include our prefix
                    Path(output_path).rename(final_output_path)
                    
                    # Add the processed file to the file manager
                    add_uploaded_file({
                        "name": output_filename,
                        "path": str(final_output_path),
                        "type": "audio",
                        "metadata": {
                            "original_file": file_info["name"],
                            "volume_level": self.settings.volume_level,
                            "normalized": self.settings.normalize,
                            "description": f"Volume adjusted: {file_info['name']}"
                        }
                    })
                    
                    # Update the output path for the results list
                    output_path = str(final_output_path)
                    results.append((file_info["name"], output_path, None))
            except Exception as e:
                results.append((file_info["name"], None, str(e)))
            
            # Update progress
            progress = (i + 1) / len(files)
            progress_bar.progress(progress)
        
        # Display results
        self._display_results(results)
        
        # Clear progress bar after a short delay
        progress_bar.empty()
    
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
            st.success(f"✅ Successfully processed {success_count} file(s)")
            
            # Show successful files
            st.write("### Processed Files")
            for filename, output_path, error in results:
                if output_path and not error:
                    st.write(f"- {filename} → {Path(output_path).name}")
        
        if error_count > 0:
            st.error(f"❌ Failed to process {error_count} file(s)")
            
            # Show error details in an expander
            with st.expander("Error Details", expanded=False):
                for filename, _, error in results:
                    if error:
                        st.error(f"**{filename}**: {error}")
        
        if success_count > 0:
            st.info("ℹ️ Processed files have been added to the file manager on the right.")
