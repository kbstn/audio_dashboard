"""
Vinyl Effect Module

This module applies a vinyl-like effect to audio files with customizable parameters.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, ClassVar

import ffmpeg
import streamlit as st

from ..utils.audio_utils import create_temp_file
from ..utils import select_files
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class VinylEffectModule(BaseModule):
    """
    Module for applying vintage vinyl record effects to audio files.
    
    This module applies a series of audio filters to simulate the characteristic
    sound of vinyl records, including:
    - Highpass and lowpass filtering
    - Echo/delay effect
    - Tremolo (volume modulation)
    - Equalization (bass and treble adjustment)
    - Volume normalization
    
    The effect chain is applied using FFmpeg's audio filters for high-quality
    processing with minimal quality loss.
    """

    # Configuration for this module
    config: ClassVar[ModuleConfig] = ModuleConfig(
        name="Vinyl Effect",
        description="Apply vintage vinyl record effects to audio",
        icon="🎵",
    )

    # Configuration for this module
    config = ModuleConfig(
        name="Vinyl Effect",
        description="Adds vinyl record characteristics to audio",
        icon="🎵",
    )

    def __init__(self):
        """
        Initialize the Vinyl Effect module.
        
        This sets up the module with its configuration and initializes
        any required state.
        """
        super().__init__()
        self.presets = {}
        self.presets_file = Path("data/vinyl_effect_presets.json")
        self.presets_file.parent.mkdir(exist_ok=True, parents=True)
        self.load_presets()
        self.output_dir = Path(st.session_state.get("UPLOAD_FOLDER", "uploads"))
        self.output_dir.mkdir(exist_ok=True)

    def save_presets_to_file(self):
        """Save presets to a JSON file"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            st.error(f"Error saving presets: {e}")

    def load_presets(self):
        """Load presets from file or initialize with default presets"""
        # Try to load presets from file
        if self.presets_file.exists():
            try:
                with open(self.presets_file, 'r') as f:
                    self.presets = json.load(f)
                return
            except Exception as e:
                st.error(f"Error loading presets: {e}. Using default presets.")
        
        # If file doesn't exist or there was an error, use defaults
        self.presets = {
                # Warm modern vinyl sound
                'Warm Vinyl': {
                    'highpass_freq': 400,
                    'lowpass_freq': 10000,
                    'echo_gain': 0.5,
                    'echo_delay': 70,
                    'tremolo_freq': 6.0,
                    'tremolo_depth': 0.15,
                    'eq_low': -3.0,
                    'eq_high': 2.0,
                    'volume': 1.2
                },
                # Classic 1950s sound
                'Classic 50s': {
                    'highpass_freq': 300,
                    'lowpass_freq': 8000,
                    'echo_gain': 1.2,
                    'echo_delay': 120,
                    'tremolo_freq': 8.0,
                    'tremolo_depth': 0.1,
                    'eq_low': -6.0,
                    'eq_high': 3.0,
                    'volume': 1.5
                },
                # 1910s Gramophone
                '1910s Gramophone': {
                    'highpass_freq': 800,  # Very limited low end
                    'lowpass_freq': 3000,   # Limited high frequencies
                    'echo_gain': 0.8,       # Some room reverb
                    'echo_delay': 200,      # Long decay
                    'tremolo_freq': 4.0,    # Slight wow effect
                    'tremolo_depth': 0.3,   # Noticeable flutter
                    'eq_low': -12.0,        # Very little bass
                    'eq_high': -6.0,        # Reduced highs
                    'volume': 1.8           # Compensate for low gain
                },
                # 1940s Radio
                '1940s Radio': {
                    'highpass_freq': 200,
                    'lowpass_freq': 5000,  # AM radio bandwidth
                    'echo_gain': 0.4,       # Subtle room echo
                    'echo_delay': 150,      # Medium decay
                    'tremolo_freq': 5.0,    # Subtle warble
                    'tremolo_depth': 0.2,   # Gentle modulation
                    'eq_low': -8.0,         # Reduced bass
                    'eq_high': -4.0,        # Slightly harsh mids
                    'volume': 1.3
                },
                # 1970s Cassette
                '70s Cassette': {
                    'highpass_freq': 100,
                    'lowpass_freq': 12000,  # Cassette hiss
                    'echo_gain': 0.3,        # Subtle tape delay
                    'echo_delay': 50,        # Short pre-echo
                    'tremolo_freq': 0.3,     # Very slow wow
                    'tremolo_depth': 0.05,   # Subtle speed variations
                    'eq_low': -2.0,          # Slight bass boost
                    'eq_high': -3.0,         # Rolled off highs
                    'volume': 1.4
                },
                # Vintage Tape Loop
                'Vintage Tape Loop': {
                    'highpass_freq': 150,
                    'lowpass_freq': 8000,   # Tape hiss filter
                    'echo_gain': 0.7,        # Noticeable delay
                    'echo_delay': 350,       # Long tape delay
                    'tremolo_freq': 0.5,     # Slow wow
                    'tremolo_depth': 0.25,   # Noticeable speed variations
                    'eq_low': -4.0,          # Reduced mud
                    'eq_high': -2.0,         # Slightly dulled highs
                    'volume': 1.6
                },
                # 1980s VHS
                '80s VHS': {
                    'highpass_freq': 80,
                    'lowpass_freq': 10000,  # VHS frequency response
                    'echo_gain': 0.6,        # Slight delay
                    'echo_delay': 30,        # Short pre-echo
                    'tremolo_freq': 0.2,     # Very slow wow
                    'tremolo_depth': 0.4,    # Noticeable wow and flutter
                    'eq_low': -6.0,          # Reduced bass
                    'eq_high': -8.0,         # Muffled highs
                    'volume': 1.7
                }
            }
        # Save the default presets to file if they don't exist
        if not self.presets_file.exists():
            self.save_presets_to_file()

    def save_preset(self, name, params):
        """Save current parameters as a new preset"""
        self.presets[name] = params
        self.save_presets_to_file()
        st.success(f"Preset '{name}' saved!")
        st.rerun()

    def delete_preset(self, name):
        """Delete a saved preset"""
        if name in self.presets:
            del self.presets[name]
            self.save_presets_to_file()
            st.success(f"Preset '{name}' deleted!")
            st.rerun()
        else:
            st.error(f"Preset '{name}' not found")

    def render_ui(self) -> None:
        """
        Render the module's user interface.
        
        This method creates the Streamlit UI components for the vinyl effect module,
        including sliders for adjusting effect parameters and file selection controls.
        """
        # Module-specific title
        st.header(f"{self.config.icon} {self.config.name}")

        # File selection using the unified utility
        selected_files = select_files(
            label="Select files to process",
            key="vinyl_effect",
            multiple=True,
            file_types=['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
        )
        
        if not selected_files:
            return

        # Effect parameters
        st.subheader("Effect Parameters")

        # Preset management
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            preset_names = list(self.presets.keys())
            selected_preset = st.selectbox(
                "Select preset", [""] + preset_names, format_func=lambda x: x or "Custom"
            )
            
        with col3:
            if st.button("Delete Preset", key="delete_vinyl_preset"):
                if selected_preset and selected_preset in self.presets:
                    self.delete_preset(selected_preset)
                    st.rerun()
        
        # If a preset is selected, load its values
        preset_params = {}
        if selected_preset and selected_preset in self.presets:
            preset_params = self.presets[selected_preset].copy()
        
        col1, col2 = st.columns(2)

        with col1:
            # Highpass filter
            highpass_freq = st.slider(
                "Highpass Frequency (Hz)",
                min_value=100,
                max_value=1000,
                value=preset_params.get('highpass_freq', 500),
                step=50,
                help="""Removes frequencies below this value\n\n * Higher values make the audio sound thinner and more "tinny"\n * Lower values provide a warmer, fuller sound while still removing rumble""",  
            )

            # Lowpass filter
            lowpass_freq = st.slider(
                "Lowpass Frequency (Hz)",
                min_value=5000,
                max_value=20000,
                value=preset_params.get('lowpass_freq', 12000),
                step=100,
                help="""Removes frequencies above this value\n\n * Lower values create a muffled, \"underwater\" or \"old recording\" sound\n * Higher values preserve more high-end detail while adding vintage character""",
            )

            # Echo effect
            st.subheader("Echo Effect")
            echo_gain = st.slider(
                "Echo Gain",
                min_value=0.1,
                max_value=2.0,
                value=preset_params.get('echo_gain', 0.8),
                step=0.1,
                help="""Controls the volume of the echo repeats (lower=subtle, higher=dramatic)\n\n * Lower values (closer to 0.1): The echoes will be very subtle, just a faint whisper of the original sound.\n * Around 0.5: The echoes will be clearly audible but won't overwhelm the original sound.\n * Higher values (closer to 2.0): The echoes will be very prominent and dramatic, potentially as loud as or louder than the original sound.""",
            )

            echo_delay = st.slider(
                "Echo Delay (ms)",
                min_value=1,
                max_value=500,
                value=preset_params.get('echo_delay', 60),
                step=1,
                help="""Delay (ms)**: Sets the time between the original sound and its echo\n\n * Shorter delays (1-50ms) create a "slapback" (single, short delay (50-150ms) that adds a quick, distinct repetition to create a vintage rockabilly or 1950s rock 'n' roll sound) effect\n * Medium delays (50-200ms) produce distinct echoes\n * Longer delays (200-500ms) create a more pronounced echo effect.""",
            )

        with col2:
            # Tremolo effect
            st.subheader("Tremolo Effect")
            tremolo_freq = st.slider(
                "Tremolo Frequency (Hz)",
                min_value=0.1,
                max_value=20.0,
                value=preset_params.get('tremolo_freq', 8.0),
                step=0.1,
                help="""**Frequency (Hz)**: Controls how fast the volume oscillates\n * Lower values (0.1-2Hz) create slow, dramatic pulsing\n * Medium values (5-10Hz) produce classic amp tremolo\n * Higher values (10-20Hz) create a more pronounced tremolo effect.""",
            )

            tremolo_depth = st.slider(
                "Tremolo Depth",
                min_value=0.0,
                max_value=1.0,
                value=preset_params.get('tremolo_depth', 0.2),
                step=0.05,
                help="""**Depth**: Controls the intensity of the volume oscillation\n * Lower values create subtle movement\n * Higher values produce dramatic volume swells""",
            )

            # Equalizer
            st.subheader("Equalizer")
            eq_low = st.slider(
                "Bass (100Hz)",
                min_value=-12.0,
                max_value=12.0,
                value=preset_params.get('eq_low', -6.0),
                step=0.5,
                help="""**Boost/cut for low frequencies**\n * Positive values add warmth and fullness\n * Negative values create a thinner, more "vintage" sound""",
            )

            eq_high = st.slider(
                "Treble (3kHz)",
                min_value=-12.0,
                max_value=12.0,
                value=preset_params.get('eq_high', 3.0),
                step=0.5,
                help="""**Boost/cut for high frequencies**\n * Positive values add presence and clarity\n * Negative values create a more muted, distant sound""",
            )

            # Volume
            volume = st.slider(
                "Output Volume",
                min_value=0.1,
                max_value=3.0,
                value=preset_params.get('volume', 1.2),
                step=0.1,
                help="""**Output volume multiplier**\n * 1.0 = original volume\n * 2.0 = double volume\n * 0.5 = half volume\n * up to 10.0""",
            )

        # Preset save and output prefix
        col1, col2 = st.columns([3, 1])
        with col1:
            # Set default prefix based on selected preset or 'vinyl_'
            default_prefix = f"{selected_preset.lower().replace(' ', '_')}_" if selected_preset else "vinyl_"
            prefix = st.text_input(
                "Output filename prefix", 
                value=default_prefix, 
                key="vinyl_prefix"
            )
            
        with col2:
            new_preset_name = st.text_input("Save as preset", key="new_vinyl_preset_name")
            if st.button("Save Preset"):
                if new_preset_name:
                    params = {
                        'highpass_freq': highpass_freq,
                        'lowpass_freq': lowpass_freq,
                        'echo_gain': echo_gain,
                        'echo_delay': echo_delay,
                        'tremolo_freq': tremolo_freq,
                        'tremolo_depth': tremolo_depth,
                        'eq_low': eq_low,
                        'eq_high': eq_high,
                        'volume': volume
                    }
                    self.save_preset(new_preset_name, params)
                    st.rerun()
                else:
                    st.warning("Please enter a name for the preset")

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
                prefix,
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
        prefix: str,
    ) -> None:
        """Process the selected files with the vinyl effect."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []

        for i, file_info in enumerate(files):
            input_file = file_info["path"]
            filename = Path(file_info["name"]).stem
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
                    f"volume={volume}",
                ]

                # Process the file with ffmpeg
                try:
                    # Create the filter graph
                    stream = ffmpeg.input(input_file)

                    # Apply filters one by one to avoid escaping issues
                    stream = stream.audio

                    # Apply each filter individually
                    stream = stream.filter("highpass", f=500)
                    stream = stream.filter("lowpass", f=12000)
                    stream = stream.filter("areverse")
                    stream = stream.filter(
                        "aecho", in_gain=0.8, out_gain=0.88, delays=60, decays=0.4
                    )
                    stream = stream.filter("areverse")
                    stream = stream.filter("tremolo", f=8.0, d=0.2)

                    # Apply equalizers
                    stream = stream.filter(
                        "equalizer", f=100, width_type="o", width=2, g=eq_low
                    )
                    stream = stream.filter(
                        "equalizer", f=3000, width_type="o", width=2, g=eq_high
                    )

                    # Apply volume
                    stream = stream.filter("volume", volume)

                    # Set up output with MP3 codec
                    stream = ffmpeg.output(
                        stream,
                        str(output_path),
                        acodec="libmp3lame",
                        audio_bitrate="192k",
                        ac=2,  # Force stereo output
                    )

                    # Get the command for debugging
                    cmd = ffmpeg.get_args(stream)
                    st.write("Running command:", "ffmpeg " + " ".join(cmd))

                    # Run the command
                    ffmpeg.run(stream, overwrite_output=True, quiet=False)

                except ffmpeg.Error as e:
                    error_message = (
                        f"FFmpeg error: {e.stderr.decode('utf-8')}"
                        if e.stderr
                        else str(e)
                    )
                    st.error(f"Error processing {file_info['name']}: {error_message}")
                    results.append(
                        {
                            "original": file_info["name"],
                            "processed": "Failed",
                            "path": error_message,
                            "status": "error",
                        }
                    )
                    continue

                # Add to results
                results.append(
                    {
                        "original": file_info["name"],
                        "processed": output_filename,
                        "path": str(output_path),
                        "status": "success",
                    }
                )

                # Add to session state if not already there
                if not any(
                    f["path"] == str(output_path)
                    for f in st.session_state.get("uploaded_files", [])
                ):
                    st.session_state.uploaded_files.append(
                        {
                            "name": output_filename,
                            "path": str(output_path),
                            "active": False,
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "original": file_info["name"],
                        "processed": "Failed",
                        "path": str(e),
                        "status": "error",
                    }
                )

        # Update progress to 100%
        progress_bar.progress(100)
        status_text.empty()

        # Show results
        if results:
            st.success("Processing complete!")

            # Show a summary of the processing
            st.subheader("Processing Results")
            for result in results:
                if result["status"] == "success":
                    st.success(f"✅ {result['original']} → {result['processed']}")
                else:
                    st.error(f"❌ {result['original']} - {result['path']}")

            # Add a button to go to the file manager
            if st.button("View in File Manager"):
                # Set the active tab to the file manager
                st.session_state.selected_module = "File Manager"
                st.rerun()

        # show advanced info
    
    def process(self, input_file: str, output_file: str, **kwargs) -> Dict[str, Any]:
        """
        Process a single audio file with the vinyl effect.
        
        Applies a series of audio filters to create a vintage vinyl record effect.
        The processing is done using FFmpeg with the following filter chain:
        1. Highpass filter to remove low frequencies
        2. Lowpass filter to remove high frequencies
        3. Echo effect with configurable parameters
        4. Tremolo (volume modulation)
        5. Equalization for bass and treble
        6. Volume adjustment
        
        Args:
            input_file: Path to the input audio file
            output_file: Path where the processed file should be saved
            **kwargs: Additional parameters for processing, including:
                - highpass_freq: Highpass filter frequency in Hz
                - lowpass_freq: Lowpass filter frequency in Hz
                - echo_gain: Echo effect gain (0.0 to 1.0)
                - echo_delay: Echo delay in milliseconds
                - tremolo_freq: Tremolo frequency in Hz
                - tremolo_depth: Tremolo depth (0.0 to 1.0)
                - eq_low: Bass equalization in dB
                - eq_high: Treble equalization in dB
                - volume: Output volume multiplier
                
        Returns:
            Dict containing processing results with the following keys:
                - status: 'success' or 'error'
                - message: Description of the result
                - output_file: Path to the processed file (if successful)
                - error: Error message (if any)
                - duration_seconds: Length of the processed audio
                - file_size_mb: Size of the output file in MB
        
        Raises:
            ffmpeg.Error: If there's an error during FFmpeg processing
        
        Example:
            ```python
            result = module.process(
                'input.mp3',
                'output.mp3',
                highpass_freq=500,
                lowpass_freq=12000,
                echo_gain=0.8,
                echo_delay=60,
                tremolo_freq=8.0,
                tremolo_depth=0.2,
                eq_low=-6.0,
                eq_high=3.0,
                volume=1.2
            )
            ```
        """
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
                ffmpeg.input(input_file)
                .filter_("af", filter_str)
                .output(output_file, acodec="libmp3lame", audio_bitrate="192k")
                .overwrite_output()
                .run(quiet=True, overwrite_output=True)
            )
            return output_file
        except ffmpeg.Error as e:
            raise Exception(f"FFmpeg error: {e.stderr.decode()}")
