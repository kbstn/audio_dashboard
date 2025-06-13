"""
Convert Audio Module

This module provides functionality to convert audio files between different formats.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, ClassVar

import streamlit as st

from ..utils.audio_utils import convert_audio
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class ConvertModule(BaseModule):
    """Module for converting audio files between different formats."""
    
    # Configuration for this module
    config: ClassVar[ModuleConfig] = ModuleConfig(
        name="Convert Audio",
        description="Convert audio files between different formats",
        icon="🔄"
    )
    """Module for converting audio files between different formats."""
    
    # Supported output formats with their display names and file extensions
    FORMATS = {
        'mp3': {'name': 'MP3', 'ext': 'mp3', 'default_bitrate': '192k'},
        'wav': {'name': 'WAV', 'ext': 'wav', 'default_bitrate': '1411k'},
        'flac': {'name': 'FLAC', 'ext': 'flac', 'default_bitrate': 'lossless'},
        'ogg': {'name': 'OGG Vorbis', 'ext': 'ogg', 'default_bitrate': '128k'},
        'm4a': {'name': 'M4A (AAC)', 'ext': 'm4a', 'default_bitrate': '192k'},
        'aac': {'name': 'AAC', 'ext': 'aac', 'default_bitrate': '192k'}
    }
    
    def __init__(self):
        """Initialize the Convert module."""
        self.output_dir = Path(st.session_state.get('UPLOAD_FOLDER', 'uploads'))
        self.output_dir.mkdir(exist_ok=True)
    
    def render_ui(self) -> None:
        """Render the conversion interface."""
        st.header("🔀 Convert Audio")
        
        # Get the list of uploaded files
        files = st.session_state.get('uploaded_files', [])
        
        if not files:
            st.warning("No audio files uploaded. Please upload files in the File Manager.")
            return
        
        # File selection
        selected_files = st.multiselect(
            "Select files to convert",
            files,
            format_func=lambda x: x['name'],
            key="convert_file_select"
        )
        
        if not selected_files:
            st.info("Please select at least one file to convert.")
            return
        
        # Output format selection
        output_format = st.selectbox(
            "Output Format",
            options=list(self.FORMATS.keys()),
            format_func=lambda x: self.FORMATS[x]['name'],
            index=0,  # Default to MP3
            key="convert_output_format"
        )
        
        # Bitrate selection (only for lossy formats)
        bitrate_options = ['128k', '192k', '256k', '320k']
        default_bitrate = self.FORMATS[output_format]['default_bitrate']
        
        if output_format in ['mp3', 'ogg', 'm4a', 'aac']:
            bitrate = st.select_slider(
                "Bitrate (higher = better quality, larger file)",
                options=bitrate_options,
                value=default_bitrate if default_bitrate in bitrate_options else '192k',
                key=f"convert_bitrate_{output_format}"
            )
        else:
            bitrate = None
        
        # Output filename prefix
        prefix = st.text_input(
            "Output filename prefix (optional)",
            value="converted_",
            key="convert_prefix"
        )
        
        # Convert button
        if st.button("Convert Files", type="primary", key="convert_button"):
            self._process_conversion(selected_files, output_format, bitrate, prefix)
    
    def _process_conversion(self, files: List[Dict], output_format: str, bitrate: Optional[str], prefix: str) -> None:
        """Process the file conversion.
        
        Args:
            files: List of file dictionaries to convert
            output_format: Target format key (e.g., 'mp3', 'wav')
            bitrate: Target bitrate (if applicable)
            prefix: Prefix for output filenames
        """
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i, file_info in enumerate(files):
            input_file = file_info['path']
            filename = Path(file_info['name']).stem
            output_ext = self.FORMATS[output_format]['ext']
            output_filename = f"{prefix}{filename}.{output_ext}"
            output_path = self.output_dir / output_filename
            
            # Update status
            progress = int((i / len(files)) * 100)
            status_text.text(f"Converting {i+1}/{len(files)}: {file_info['name']}")
            progress_bar.progress(progress)
            
            try:
                # Convert the file
                output_file = convert_audio(
                    input_file=input_file,
                    output_file=str(output_path),
                    format=output_format,
                    bitrate=bitrate if bitrate else None
                )
                
                # Add to results
                results.append({
                    'original': file_info['name'],
                    'converted': output_filename,
                    'path': str(output_file),
                    'status': 'success'
                })
                
                # Add to session state if not already there
                if not any(f['path'] == str(output_file) for f in st.session_state.get('uploaded_files', [])):
                    st.session_state.uploaded_files.append({
                        'name': output_filename,
                        'path': str(output_file),
                        'active': False
                    })
                
            except Exception as e:
                results.append({
                    'original': file_info['name'],
                    'converted': 'Failed',
                    'path': str(e),
                    'status': 'error'
                })
        
        # Update progress to 100%
        progress_bar.progress(100)
        status_text.empty()
        
        # Show results
        if results:
            st.success("Conversion complete!")
            
            # Show a summary of the conversion
            st.subheader("Conversion Results")
            for result in results:
                if result['status'] == 'success':
                    st.success(f"✅ {result['original']} → {result['converted']}")
                else:
                    st.error(f"❌ {result['original']} - {result['path']}")
            
            # Add a button to go to the file manager
            if st.button("View in File Manager"):
                # Set the active tab to the file manager
                st.session_state.selected_module = "File Manager"
                st.rerun()
    
    def process(self, input_file: str) -> str:
        """Process a single file (required by BaseModule)."""
        # This is a simplified version for programmatic use
        output_file = str(Path(input_file).with_suffix('.converted.mp3'))
        return convert_audio(
            input_file=input_file,
            output_file=output_file,
            format='mp3',
            bitrate='192k'
        )
