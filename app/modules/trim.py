"""
Trim module for the Audio Processing Dashboard.

This module provides functionality to trim audio files.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

import streamlit as st
from pydantic import BaseModel, Field, validator

from ..utils import get_audio_info, trim_audio, create_temp_file, delete_file
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class TrimModule(BaseModule):
    """Module for trimming audio files."""

    config = ModuleConfig(
        name="Trim Audio",
        description="Trim audio files by selecting start and end times",
        icon="✂️",
    )

    class Settings(BaseModel):
        """Settings for the Trim module."""

        start_time: float = Field(0.0, ge=0.0, description="Start time in seconds")
        end_time: float = Field(10.0, ge=0.1, description="End time in seconds")

        @validator("end_time")
        def validate_end_time(cls, v, values):
            if "start_time" in values and v <= values["start_time"]:
                raise ValueError("End time must be greater than start time")
            return v

    def __init__(self):
        """Initialize the module with default settings."""
        super().__init__()
        self.settings = self.Settings()
        self.audio_info: Dict[str, Any] = {}
        self.output_file: Optional[str] = None

    def _get_audio_info(self, filepath: str) -> Dict[str, Any]:
        """Get information about the audio file.

        Args:
            filepath: Path to the audio file.

        Returns:
            Dictionary containing audio file information.
        """
        if not self.audio_info or self.audio_info.get("path") != filepath:
            self.audio_info = get_audio_info(filepath)
        return self.audio_info

    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS.mmm format.

        Args:
            seconds: Time in seconds.

        Returns:
            Formatted time string.
        """
        minutes = int(seconds // 60)
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:06.3f}"

    def render_ui(self) -> None:
        """Render the module's user interface."""
        st.markdown(f"# {self.config.icon} {self.config.name}")

        # Get the active file from session state
        active_file = st.session_state.get("active_file")

        if not active_file:
            st.warning("Please upload and select an audio file first.")
            return

        # Get audio file info
        try:
            audio_info = self._get_audio_info(active_file)
            if not audio_info:
                st.error("Could not read audio file information.")
                return

            duration = float(audio_info.get("duration", 0))
            if duration <= 0:
                st.error("Invalid audio duration.")
                return

            # Display file info
            st.write(f"**File:** {Path(active_file).name}")
            st.write(f"**Duration:** {self._format_time(duration)}")
            st.write(f"**Sample Rate:** {audio_info.get('sample_rate', 0)} Hz")
            st.write(f"**Channels:** {audio_info.get('channels', 0)}")
            st.write(f"**Format:** {audio_info.get('format', 'Unknown').upper()}")

            # Time selection sliders
            col1, col2 = st.columns(2)

            with col1:
                self.settings.start_time = st.slider(
                    "Start Time",
                    min_value=0.0,
                    max_value=min(duration - 0.1, 3600),  # Cap at 1 hour
                    value=0.0,
                    step=0.1,
                    format="%.1f s",
                )

            with col2:
                max_end = min(
                    duration, self.settings.start_time + 3600
                )  # Cap at 1 hour from start
                self.settings.end_time = st.slider(
                    "End Time",
                    min_value=min(self.settings.start_time + 0.1, max_end),
                    max_value=max_end,
                    value=min(
                        duration, self.settings.start_time + 30
                    ),  # Default 30s clip
                    step=0.1,
                    format="%.1f s",
                )

            # Display selection info
            st.write(
                f"**Selection:** {self._format_time(self.settings.start_time)} - {self._format_time(self.settings.end_time)} "
                f"(Duration: {self._format_time(self.settings.end_time - self.settings.start_time)})"
            )

            # Process button
            if st.button("Trim Audio"):
                with st.spinner("Trimming audio..."):
                    try:
                        # Get the input file extension for the output
                        output_ext = Path(active_file).suffix.lstrip(".")

                        # Trim the audio (let trim_audio handle the output file creation)
                        self.output_file = trim_audio(
                            input_file=active_file,
                            output_file=None,  # Let trim_audio create the temp file
                            start_time=self.settings.start_time,
                            end_time=self.settings.end_time,
                            format=output_ext or None,  # Pass None to use input format
                        )

                        # Display success message
                        st.success("Audio trimmed successfully!")

                        # Display audio player
                        st.audio(self.output_file)

                        # Add the trimmed file to the file list
                        trimmed_filename = f"trimmed_{Path(active_file).name}"
                        trimmed_file_info = {
                            "name": trimmed_filename,
                            "path": self.output_file,
                            "active": False,
                        }

                        # Add to the beginning of the list and make it active
                        if "uploaded_files" not in st.session_state:
                            st.session_state.uploaded_files = []

                        st.session_state.uploaded_files.insert(0, trimmed_file_info)

                        # Set the new file as active
                        for f in st.session_state.uploaded_files:
                            f["active"] = False
                        trimmed_file_info["active"] = True
                        st.session_state.active_file = self.output_file

                        # Add download button
                        output_ext = Path(self.output_file).suffix.lstrip(".")
                        mime_type = f"audio/{output_ext}" if output_ext else "audio/wav"

                        st.success(
                            "Audio trimmed successfully! The trimmed file has been added to your file list."
                        )

                        with open(self.output_file, "rb") as f:
                            st.download_button(
                                label="Download Trimmed Audio",
                                data=f,
                                file_name=trimmed_filename,
                                mime=mime_type,
                            )

                    except Exception as e:
                        # Clean up the output file if it exists
                        if self.output_file and os.path.exists(self.output_file):
                            delete_file(self.output_file)
                            self.output_file = None
                        st.error(f"Error trimming audio: {str(e)}")

        except Exception as e:
            st.error(f"Error: {str(e)}")

    def process(self, input_file: str) -> str:
        """
        Process the audio file with the current settings.

        Args:
            input_file: Path to the input audio file.

        Returns:
            Path to the processed audio file.
        """
        if not self.output_file or not os.path.exists(self.output_file):
            raise ValueError("No trimmed audio available. Please trim the audio first.")

        return self.output_file
