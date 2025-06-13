# Audio Processing Dashboard

A modular audio processing dashboard built with Streamlit, designed for applying various audio effects and transformations using FFmpeg.

## 🚀 Features

- 🎵 **File Management**
  - Upload multiple audio files (WAV, MP3, OGG, FLAC, M4A, AAC)
  - Reorder files with up/down buttons
  - Delete individual files with confirmation
  - Clear all files at once
  - Active file highlighting
  - Download processed files

- ✂️ **Audio Processing**
  - Trim audio with visual timeline
  - Preview audio before processing
  - Preserve original file format
  - Real-time feedback

- 🎛️ **Modular Architecture**
  - Easy to add new processing modules
  - Consistent UI/UX across modules
  - Isolated module functionality

- 🎧 **User Experience**
  - Three-column responsive layout
  - Intuitive controls
  - Visual feedback for all actions
  - Error handling and user notifications

## Getting Started

### Prerequisites

- Python 3.11 (LTS - Long Term Support)
- FFmpeg
- micromamba (recommended) or conda

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ffmpeg_dashboard2
   ```

2. Create and activate the conda environment:
   ```bash
   micromamba create -n audio_dashboard python=3.9
   micromamba activate audio_dashboard
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
streamlit run app/main.py
```

## Project Structure

```
ffmpeg_dashboard/
├── app/                    # Main application package
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Main application entry point
│   ├── config.py           # Application configuration
│   ├── session_state.py    # Session state management
│   ├── utils/              # Utility functions
│   └── modules/            # Audio processing modules
├── tests/                  # Test files
├── uploads/                # Uploaded files (created at runtime)
├── .env                   # Environment variables (create manually)
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Adding New Modules

1. Create a new Python file in `app/modules/`
2. Create a class that inherits from `BaseModule`
3. Implement the required methods
4. The module will be automatically discovered and added to the UI

Example module:

```python
from .base_module import BaseModule, ModuleConfig

class MyModule(BaseModule):
    config = ModuleConfig(
        name="My Module",
        description="A brief description of what this module does",
        icon="🎛️"
    )
    
    def render_ui(self):
        st.write("Configure your module here")
        # Add your UI components here
    
    def process(self, input_file: str) -> str:
        # Process the input file and return the output file path
        return input_file  # Replace with actual processing
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing dashboard framework
- [FFmpeg](https://ffmpeg.org/) for powerful audio processing
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
