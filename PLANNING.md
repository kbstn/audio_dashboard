
## Project Structure
```
ffmpeg_dashboard2/
├── app/
│   ├── __init__.py
│   ├── main.py             # Main application entry point
│   ├── config.py           # Configuration and constants
│   ├── session_state.py    # Session state management
│   ├── utils/              # Utility functions
│   │   ├── __init__.py
│   │   └── audio_utils.py  # Audio processing utilities
│   └── modules/            # Individual processing modules
│       ├── __init__.py     # Module registration
│       ├── base_module.py  # Base module class
│       ├── trim.py         # Audio trimming module
│       └── about.py        # About page module
├── uploads/                # Uploaded and processed files
├── tests/                  # Unit tests
├── .gitignore
├── requirements.txt        # Python dependencies
├── README.md
└── PLANNING.md
```

## Project Summary
A modular, user-friendly dashboard for audio file processing built with Streamlit. This application enables users to upload audio files, apply various FFmpeg-based transformations, and download the processed files. The architecture is designed for extensibility, allowing easy addition of new processing modules.

## Development Environment
- **Virtual Environment**: micromamba (required)
- **Package Manager**: micromamba (preferred) or conda
- **Python Version**: 3.11 (LTS - Long Term Support)

### Getting Started with micromamba
1. Install micromamba if not already installed
2. Create and activate the environment:
   ```bash
   micromamba create -n audio_dashboard python=3.9
   micromamba activate audio_dashboard
   ```
3. Install dependencies:
   ```bash
   micromamba install -c conda-forge streamlit pydub pydantic ffmpeg-python python-dotenv
   ```
4. Run the app:
   ```bash
   streamlit run app/main.py
   ```

## Core Features
- Audio file upload and management
- Modular processing pipeline
- Session state management
- Audio playback and preview
- Result download

## Development Phases

### Phase 1: Core Structure (Completed)
- [x] Set up Streamlit app with three-column layout
- [x] Implement file uploader in right sidebar
- [x] Create file management system with global file access
- [x] Set up session state management
- [x] Add file upload/download functionality
- [x] Implement file reordering and deletion
- [x] Add active file tracking
- [x] Create responsive UI components

### Phase 2: Module System (In Progress)
- [x] Create base module class
- [x] Implement module registration system
- [x] Develop trim module with UI
- [x] Add about page module
- [ ] Add audio visualization module
- [ ] Implement audio effects module
- [ ] Add batch processing capabilities

### Phase 3: Enhanced Features (Planned)
- [ ] Audio visualization with waveform display
- [ ] Batch processing for multiple files
- [ ] Keyboard shortcuts for common actions
- [ ] Audio analysis tools
- [ ] Support for more audio formats
- [ ] Advanced audio effects
- [ ] Export presets for common workflows

### Phase 4: Enhanced Features
- [ ] Add audio visualization
- [ ] Implement batch processing
- [ ] Add keyboard shortcuts
- [ ] Include audio analysis tools

## Development Guidelines

### Code Organization
- Keep modules small and focused (max 250 lines)
- Separate business logic from UI code
- Use type hints and Google-style docstrings
- Implement comprehensive error handling
- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add comments for complex logic

### Module Development
1. Create a new file in `app/modules/`
2. Import and extend `BaseModule`
3. Implement required methods
4. Register the module in `app/modules/__init__.py`
5. Add module-specific CSS if needed
6. Test thoroughly with different audio formats

### Testing
- Write unit tests for all utility functions
- Test with various audio formats
- Verify UI responsiveness
- Test error conditions
- Document test cases

### Streamlit Specific
- Use session state for maintaining state
- Cache expensive computations
- Implement proper widget keys
- Use columns and containers for responsive layouts

### Performance
- Process large files asynchronously
- Implement proper cleanup of temporary files
- Use generators for large file processing
- Cache intermediate results when possible

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app/main.py`

## Dependencies
- streamlit
- pydub
- pydantic
- ffmpeg-python
- python-dotenv

## Future Enhancements
- User authentication
- Cloud storage integration
- Preset configurations
- Plugin system for custom modules