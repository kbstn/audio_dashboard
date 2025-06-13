"""
Vinyl Effect Module

This module applies a vinyl-like effect to audio files with customizable parameters.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, ClassVar

import ffmpeg
import streamlit as st

from ..utils.audio_utils import create_temp_file
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class VinylEffectModule(BaseModule):
    """Module for applying vinyl-like effects to audio files."""
    
    # Configuration for this module
    config: ClassVar[ModuleConfig] = ModuleConfig(
        name="Vinyl Effect",
        description="Apply vintage vinyl record effects to audio",
        icon="🎵"
    )
    
    def __init__(self):
        """Initialize the Vinyl Effect module."""
        self.output_dir = Path(st.session_state.get('UPLOAD_FOLDER', 'uploads'))
        self.output_dir.mkdir(exist_ok=True)
    
    def render_ui(self) -> None:
        """Render the vinyl effect interface."""
        st.header("🎵 Vinyl Effect")
        
        # Get the list of uploaded files
        files = st.session_state.get('uploaded_files', [])
        
        if not files:
            st.warning("No audio files uploaded. Please upload files in the File Manager.")
            return
        
        # File selection
        selected_files = st.multiselect(
            "Select files to process",
            files,
            format_func=lambda x: x['name'],
            key="vinyl_file_select"
        )
        
        if not selected_files:
            st.info("Please select at least one file to process.")
            return
        
        # Effect parameters
        st.subheader("Effect Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Highpass filter
            highpass_freq = st.slider(
                "Highpass Frequency (Hz)",
                min_value=100,
                max_value=1000,
                value=500,
                step=50,
                help="Removes frequencies below this value"
            )
            
            # Lowpass filter
            lowpass_freq = st.slider(
                "Lowpass Frequency (Hz)",
                min_value=5000,
                max_value=20000,
                value=12000,
                step=100,
                help="Removes frequencies above this value"
            )
            
            # Echo effect
            st.subheader("Echo Effect")
            echo_gain = st.slider(
                "Echo Gain",
                min_value=0.1,
                max_value=2.0,
                value=0.8,
                step=0.1,
                help="Echo signal volume"
            )
            
            echo_delay = st.slider(
                "Echo Delay (ms)",
                min_value=1,
                max_value=500,
                value=60,
                step=1,
                help="Delay between echoes in milliseconds"
            )
        
        with col2:
            # Tremolo effect
            st.subheader("Tremolo Effect")
            tremolo_freq = st.slider(
                "Tremolo Frequency (Hz)",
                min_value=0.1,
                max_value=20.0,
                value=8.0,
                step=0.1,
                help="Frequency of the volume modulation"
            )
            
            tremolo_depth = st.slider(
                "Tremolo Depth",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
                help="Depth of the volume modulation"
            )
            
            # Equalizer
            st.subheader("Equalizer")
            eq_low = st.slider(
                "Bass (100Hz)",
                min_value=-12.0,
                max_value=12.0,
                value=-6.0,
                step=0.5,
                help="Boost/cut for low frequencies"
            )
            
            eq_high = st.slider(
                "Treble (3kHz)",
                min_value=-12.0,
                max_value=12.0,
                value=3.0,
                step=0.5,
                help="Boost/cut for high frequencies"
            )
            
            # Volume
            volume = st.slider(
                "Output Volume",
                min_value=0.1,
                max_value=3.0,
                value=1.2,
                step=0.1,
                help="Output volume multiplier"
            )
        
        # Output filename prefix
        prefix = st.text_input(
            "Output filename prefix",
            value="vinyl_",
            key="vinyl_prefix"
        )
        
        # Process button
        if st.button("Apply Vinyl Effect", type="primary", key="vinyl_apply"):
            self._process_files(
                selected_files,
                highpass_freq,
                lowpass_freq,
                echo_gain,
                echo_delay,
                tremolo_freq,
                tremolo_depth,
                eq_low,
                eq_high,
                volume,
                prefix
            )
    
    def _process_files(
        self,
        files: List[Dict],
        highpass_freq: int,
        lowpass_freq: int,
        echo_gain: float,
        echo_delay: int,
        tremolo_freq: float,
        tremolo_depth: float,
        eq_low: float,
        eq_high: float,
        volume: float,
        prefix: str
    ) -> None:
        """Process the selected files with the vinyl effect."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i, file_info in enumerate(files):
            input_file = file_info['path']
            filename = Path(file_info['name']).stem
            output_filename = f"{prefix}{filename}.mp3"
            output_path = self.output_dir / output_filename
            
            # Update status
            progress = int((i / len(files)) * 100)
            status_text.text(f"Processing {i+1}/{len(files)}: {file_info['name']}")
            progress_bar.progress(progress)
            
            try:
                # Build the filter graph
                filter_chain = [
                    # Highpass filter
                    f"highpass=f={highpass_freq}",
                    # Lowpass filter
                    f"lowpass=f={lowpass_freq}",
                    # Reverse for echo
                    "areverse",
                    # Echo effect
                    f"aecho={echo_gain}:0.88:{echo_delay}:0.4",
                    # Reverse back
                    "areverse",
                    # Tremolo effect
                    f"tremolo=f={tremolo_freq}:d={tremolo_depth}",
                    # Equalizer (bass)
                    f"equalizer=f=100:width_type=o:width=2:g={eq_low}",
                    # Equalizer (treble)
                    f"equalizer=f=3000:width_type=o:width=2:g={eq_high}",
                    # Volume adjustment
                    f"volume={volume}"
                ]
                
                # Process the file with ffmpeg
                try:
                    # Create the filter graph
                    stream = ffmpeg.input(input_file)
                    
                    # Apply filters one by one to avoid escaping issues
                    stream = stream.audio
                    
                    # Apply each filter individually
                    stream = stream.filter('highpass', f=500)
                    stream = stream.filter('lowpass', f=12000)
                    stream = stream.filter('areverse')
                    stream = stream.filter('aecho', in_gain=0.8, out_gain=0.88, delays=60, decays=0.4)
                    stream = stream.filter('areverse')
                    stream = stream.filter('tremolo', f=8.0, d=0.2)
                    
                    # Apply equalizers
                    stream = stream.filter('equalizer', f=100, width_type='o', width=2, g=eq_low)
                    stream = stream.filter('equalizer', f=3000, width_type='o', width=2, g=eq_high)
                    
                    # Apply volume
                    stream = stream.filter('volume', volume)
                    
                    # Set up output with MP3 codec
                    stream = ffmpeg.output(
                        stream,
                        str(output_path),
                        acodec='libmp3lame',
                        audio_bitrate='192k',
                        ac=2  # Force stereo output
                    )
                    
                    # Get the command for debugging
                    cmd = ffmpeg.get_args(stream)
                    st.write("Running command:", 'ffmpeg ' + ' '.join(cmd))
                    
                    # Run the command
                    ffmpeg.run(stream, overwrite_output=True, quiet=False)
                    
                    
                except ffmpeg.Error as e:
                    error_message = f"FFmpeg error: {e.stderr.decode('utf-8')}" if e.stderr else str(e)
                    st.error(f"Error processing {file_info['name']}: {error_message}")
                    results.append({
                        'original': file_info['name'],
                        'processed': 'Failed',
                        'path': error_message,
                        'status': 'error'
                    })
                    continue
                
                # Add to results
                results.append({
                    'original': file_info['name'],
                    'processed': output_filename,
                    'path': str(output_path),
                    'status': 'success'
                })
                
                # Add to session state if not already there
                if not any(f['path'] == str(output_path) for f in st.session_state.get('uploaded_files', [])):
                    st.session_state.uploaded_files.append({
                        'name': output_filename,
                        'path': str(output_path),
                        'active': False
                    })
                
            except Exception as e:
                results.append({
                    'original': file_info['name'],
                    'processed': 'Failed',
                    'path': str(e),
                    'status': 'error'
                })
        
        # Update progress to 100%
        progress_bar.progress(100)
        status_text.empty()
        
        # Show results
        if results:
            st.success("Processing complete!")
            
            # Show a summary of the processing
            st.subheader("Processing Results")
            for result in results:
                if result['status'] == 'success':
                    st.success(f"✅ {result['original']} → {result['processed']}")
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
        output_file = str(Path(input_file).with_name(f"vinyl_{Path(input_file).name}"))
        
        # Default vinyl effect
        filter_str = (
            "highpass=f=500,lowpass=f=12000,"
            "areverse,aecho=0.8:0.88:60:0.4,areverse,"
            "tremolo=f=8:d=0.2,"
            "equalizer=f=100:width_type=o:width=2:g=-6,"
            "equalizer=f=3000:width_type=o:width=2:g=3,"
            "volume=1.2"
        )
        
        try:
            (
                ffmpeg
                .input(input_file)
                .filter_('af', filter_str)
                .output(output_file, acodec='libmp3lame', audio_bitrate='192k')
                .overwrite_output()
                .run(quiet=True, overwrite_output=True)
            )
            return output_file
        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg error: {e.stderr.decode()}")
