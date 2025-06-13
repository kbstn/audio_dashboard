# Audio Dashboard Module Development Guide

This guide explains how to create new modules for the Audio Dashboard.

## 1. Module Structure

```python
"""Brief module description."""
from pathlib import Path
from typing import Any, Dict, List
import streamlit as st
from .base_module import BaseModule, ModuleConfig, register_module
from ..utils import select_files  # For file selection

@register_module
class YourModule(BaseModule):
    """One-line module description."""
    
    config = ModuleConfig(
        name="Module Name",
        description="What this module does",
        icon="🎵",  # Choose an emoji
    )
    
    def __init__(self):
        super().__init__()
        # Initialize state here
        
    def render_ui(self) -> None:
        """Build the module's UI."""
        st.header(f"{self.config.icon} {self.config.name}")
        
        # 1. File selection
        files = select_files(
            "Select files",
            key="your_module_key",
            multiple=True,  # or False
            file_types=['.mp3', '.wav']
        )
        if not files:
            return
            
        # 2. Add your controls here
        
        # 3. Process button
        if st.button("Process"):
            self.process_files(files)
    
    def process(self, input_file: str) -> str:
        """Process one file. Return output path."""
        # Your processing logic here
        return output_path
```

## 2. Key Points

- **File Selection**: Use `select_files()` for consistent file picking
- **UI**: Keep it clean with Streamlit widgets
- **Processing**: Implement both single (`process()`) and batch processing
- **Errors**: Handle and display errors clearly
- **State**: Store UI state in `__init__`
- **Types**: Use type hints for better code quality

## 3. Best Practices

- Keep modules under 250 lines
- Split complex logic into methods
- Add docstrings to public methods
- Test with different file formats
- Follow existing code style

## 4. Example: Simple Module

```python
@register_module
class VolumeControl(BaseModule):
    """Adjust audio volume."""
    
    config = ModuleConfig(
        name="Volume Control",
        description="Change audio volume level",
        icon="🔊",
    )
    
    def __init__(self):
        super().__init__()
        self.volume = 1.0
        
    def render_ui(self) -> None:
        st.header(f"{self.config.icon} {self.config.name}")
        
        files = select_files("Select audio", "volume_control", True, ['.mp3', '.wav'])
        if not files:
            return
            
        self.volume = st.slider("Volume", 0.1, 3.0, 1.0, 0.1)
        
        if st.button("Adjust Volume"):
            self.process_files(files)
    
    def process(self, input_file: str) -> str:
        output_file = create_temp_file(suffix=".wav")
        # FFmpeg volume adjustment here
        return output_file
```

For more examples, see existing modules in the `app/modules/` directory.
