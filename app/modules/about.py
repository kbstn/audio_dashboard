"""
About Module

Displays information about the Audio Processing Dashboard.
"""
import streamlit as st
from pathlib import Path
from .base_module import BaseModule, ModuleConfig, register_module


@register_module
class AboutModule(BaseModule):
    """About module that displays application information."""

    config = ModuleConfig(name="About", description="About this application", icon="ℹ️")

    def render_ui(self) -> None:
        """Render the about page UI."""
        st.markdown(f"# {self.config.icon} {self.config.name}")
        st.markdown("### Audio Processing Dashboard")
        st.markdown("A modular dashboard for audio processing using FFmpeg.")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Features")
            st.markdown(
                """
            - 🎵 Upload and manage audio files
            - ✂️ Trim and edit audio
            - 🎚️ Apply various audio effects
            - 💾 Export processed files
            - 🧩 Extensible module system
            """
            )

        with col2:
            st.markdown("### Getting Started")
            st.markdown(
                """
            1. Upload an audio file using the sidebar
            2. Select a module from the left sidebar
            3. Adjust the settings as needed
            4. Process and download your audio
            """
            )

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            """
        This application is built with:
        - [Streamlit](https://streamlit.io/)
        - [FFmpeg](https://ffmpeg.org/)
        - [Pydantic](https://pydantic-docs.helpmanual.io/)
        - [Pydub](https://github.com/jiaaro/pydub)
        
        Source code available on [GitHub](https://github.com/yourusername/ffmpeg-dashboard).
        """
        )

    def process(self, input_file: str) -> str:
        """
        Process the input file (not used for the about page).

        Args:
            input_file: Path to the input file

        Returns:
            Path to the output file (same as input for this module)
        """
        return input_file
