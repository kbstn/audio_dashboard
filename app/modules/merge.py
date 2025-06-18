"""
Merge Audio Module

This module provides functionality to merge multiple audio files into a single file.
"""
from pathlib import Path
from typing import Dict, List, Optional, ClassVar

import streamlit as st

from ..utils.audio_utils import merge_audio
from ..utils import select_files
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class MergeModule(BaseModule):
    """Module for merging multiple audio files into one."""

    # Configuration for this module
    config: ClassVar[ModuleConfig] = ModuleConfig(
        name="Merge Audio",
        description="Merge multiple audio files into a single file",
        icon="🔊",
    )

    # Supported output formats with their display names and file extensions
    FORMATS = {
        "mp3": {"name": "MP3", "ext": "mp3"},
        "wav": {"name": "WAV", "ext": "wav"},
        "flac": {"name": "FLAC", "ext": "flac"},
        "ogg": {"name": "OGG Vorbis", "ext": "ogg"},
        "m4a": {"name": "M4A (AAC)", "ext": "m4a"},
    }

    def __init__(self):
        """Initialize the Merge module."""
        self.output_dir = Path(st.session_state.get("UPLOAD_FOLDER", "uploads"))
        self.output_dir.mkdir(exist_ok=True)

    def render_ui(self) -> None:
        """Render the merge interface."""
        st.header("🔊 Merge Audio")

        # File selection using the unified utility
        st.caption("Select multiple audio files to merge. The order of selection determines the merge order.")
        selected_files = select_files(
            label="Select audio files to merge (in order)",
            key="merge_files",
            multiple=True,
            file_types=['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac']
        )

        if not selected_files:
            st.info("Please select at least one audio file to merge.")
            return

        # Output format selection
        output_format = st.selectbox(
            "Output Format",
            options=list(self.FORMATS.keys()),
            format_func=lambda x: self.FORMATS[x]["name"],
            help="Select the output format for the merged file.",
        )

        # Output filename
        output_filename = st.text_input(
            "Output Filename (without extension)",
            value="merged_audio",
            help="Enter a name for the merged file (without extension).",
        )

        # Process button
        if st.button("Merge Audio"):
            with st.spinner("Merging audio files..."):
                try:
                    # Get the output path
                    output_ext = self.FORMATS[output_format]["ext"]
                    output_path = self.output_dir / f"{output_filename}.{output_ext}"

                    # Get the list of input file paths in order
                    input_files = [file_info["path"] for file_info in selected_files]

                    # Merge the files
                    result_path = merge_audio(
                        input_files=input_files,
                        output_file=str(output_path),
                        output_format=output_format,
                    )

                    # Update the file list in session state
                    if not hasattr(st.session_state, "uploaded_files"):
                        st.session_state.uploaded_files = []

                    # Add the merged file to the file manager
                    if not any(f["path"] == result_path for f in st.session_state.uploaded_files):
                        st.session_state.uploaded_files.append(
                            {
                                "name": f"{output_filename}.{output_ext}",
                                "path": result_path,
                                "active": False,
                            }
                        )

                    st.success(f"Successfully merged {len(selected_files)} files!")
                    st.audio(result_path)

                    # Provide download button
                    with open(result_path, "rb") as f:
                        st.download_button(
                            label="Download Merged File",
                            data=f,
                            file_name=f"{output_filename}.{output_ext}",
                            mime=f"audio/{output_format}",
                        )

                except Exception as e:
                    st.error(f"Error merging audio files: {str(e)}")

    def process(self, input_file: str) -> None:
        """Process a single file (required by BaseModule).
        
        This module doesn't support single file processing, so we'll just pass.
        """
        pass
