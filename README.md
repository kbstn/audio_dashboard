# DISCLAIMER: 

This project is a test to find out about windsurf ide possibillities, i soley used the SWE-1 free model and tried not to write any code or documentation by hand. I managed to create a dockerized streamlit app with ffmpeg support and a modular audio processing dashboard, which is not as i wanted it still works and does the job. Even though i tried to railguard it with rules and planning and task files the agent often lost overview of the project and wrote a lot of bloat code. A lot of stuff might simply be made up by the agent ;-)


# 🎵 FFmpeg Audio Processing Dashboard

A powerful, modular audio processing dashboard built with Streamlit and FFmpeg, designed for applying various audio effects and transformations with an intuitive web interface.

## 🌟 Features

### 🎛️ Audio Processing Modules
- **Volume Control** - Adjust volume levels and normalize audio across files
- **Format Conversion** - Convert between various audio formats (MP3, WAV, OGG, FLAC, M4A, AAC)
- **Audio Trimming** - Cut and trim audio files with precision
- **Audio Merging** - Combine multiple audio files into one
- **Vinyl Effect** - Apply vintage vinyl record effects to your audio

### 🗂️ File Management
- Upload multiple audio files (WAV, MP3, OGG, FLAC, M4A, AAC)
- Preview audio files before processing
- Download processed files directly from the interface
- Persistent file storage between sessions

### 🎨 User Interface
- Clean, responsive design
- Real-time audio visualization
- Intuitive module-based workflow
- Dark/light theme support

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed on your system
- Git (for cloning the repository)

### Using the Deployment Script (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/kbstn/ffmpeg_dashboard.git
   cd ffmpeg_dashboard
   ```

2. Make the deployment script executable and run it:
   ```bash
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

3. Follow the interactive prompts to configure your setup

4. Access the dashboard at `http://localhost:8508`

### Manual Docker Deployment

1. Clone the repository:
   ```bash
   git clone https://github.com/kbstn/ffmpeg_dashboard.git
   cd ffmpeg_dashboard
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to change any settings if necessary.

3. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

4. Access the dashboard at `http://localhost:8508`

## 🐳 Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose up -d` | Start the containers in detached mode |
| `docker-compose down` | Stop and remove the containers |
| `docker-compose logs -f` | View container logs |
| `docker-compose up -d --build` | Rebuild and restart containers |
| `docker-compose exec app bash` | Open a shell in the running container |

## 📂 Project Structure

```
ffmpeg_dashboard/
├── app/                    # Main application code
│   ├── modules/            # Audio processing modules
│   ├── utils/              # Utility functions
│   ├── config.py           # Application configuration
│   ├── main.py             # Main application entry point
│   └── session_state.py    # Session state management
├── data/                   # Data files and presets
├── uploads/                # User-uploaded files (persistent volume)
├── .env.example           # Example environment variables
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile             # Docker image definition
└── requirements.txt       # Python dependencies
```

## 🛠️ Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/kbstn/ffmpeg_dashboard.git
   cd ffmpeg_dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install FFmpeg (required for audio processing):
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

5. Run the development server:
   ```bash
   streamlit run app/main.py
   ```

### Creating New Modules

To create a new audio processing module:

1. Create a new Python file in `app/modules/`
2. Define your module class that inherits from `BaseModule`
3. Use the `@register_module` decorator to register your module

Example module structure:

```python
from .base_module import BaseModule, register_module, ModuleConfig

@register_module
class MyModule(BaseModule):
    config = ModuleConfig(
        name="My Module",
        description="A brief description of what this module does",
        icon="🎛️"
    )
    
    def __init__(self):
        super().__init__()
        # Initialize your module here
    
    def render_ui(self):
        # Render your module's UI here
        pass
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FFmpeg](https://ffmpeg.org/) - For the powerful audio/video processing
- [Streamlit](https://streamlit.io/) - For the amazing web app framework
- [Python](https://www.python.org/) - For being awesome

