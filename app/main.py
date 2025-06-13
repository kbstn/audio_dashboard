"""
Main entry point for the Audio Processing Dashboard.

This module initializes the Streamlit application and sets up the main UI layout.
"""
import os
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, Any

# Add the app directory to the path so we can import the modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.config import APP_NAME, VERSION, UPLOAD_FOLDER
from app.session_state import (
    init_session_state, 
    get_uploaded_files, 
    set_active_file, 
    get_active_file,
    add_uploaded_file,
    remove_uploaded_file
)
from app.modules import MODULES

def init() -> None:
    """Initialize the application."""
    init_session_state()
    
    # Create uploads directory if it doesn't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
    
    # Set page config
    st.set_page_config(
        page_title=f"{APP_NAME} {VERSION}",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_module_sidebar() -> None:
    """Render the left sidebar with module selection."""
    st.sidebar.title("🎛️ Modules")
    
    # Get the list of available modules
    module_names = list(MODULES.keys())
    selected_module_name = st.sidebar.radio(
        "Select a module:",
        module_names,
        index=0,
        key="selected_module"
    )
    
    # Add some spacing
    st.sidebar.markdown("---")
    
    # Add app info
    st.sidebar.markdown(f"**{APP_NAME}** v{VERSION}")
    st.sidebar.markdown("*Audio processing made easy*")

def save_uploaded_file(uploaded_file) -> Path:
    """
    Save an uploaded file to the uploads directory and return its path.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        
    Returns:
        Path: The path where the file was saved
    """
    # Create uploads directory if it doesn't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
    
    # Create a path to save the file
    file_path = UPLOAD_FOLDER / uploaded_file.name
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path

def render_file_sidebar() -> None:
    """Render the right sidebar with file upload and list."""
    st.title("📁 File Manager")
    
    # File uploader in the sidebar - only for selecting files
    uploaded_files = st.file_uploader(
        "Add audio files",
        type=["wav", "mp3", "ogg", "flac", "m4a", "aac"],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    # Process newly uploaded files
    if uploaded_files and len(uploaded_files) > 0:
        # Use a flag to track if we've processed new files
        if 'last_processed_files' not in st.session_state:
            st.session_state.last_processed_files = set()
        
        # Get the current set of uploaded files
        current_files = {f.name for f in uploaded_files}
        
        # Only process new files that haven't been processed yet
        new_files = [f for f in uploaded_files if f.name not in st.session_state.last_processed_files]
        
        if new_files:
            for uploaded_file in new_files:
                # Skip if file already exists in our list
                if any(f['name'] == uploaded_file.name for f in get_uploaded_files()):
                    continue
                    
                # Save to temp file
                file_path = save_uploaded_file(uploaded_file)
                
                # Create new file info
                file_info = {
                    'name': uploaded_file.name,
                    'path': str(file_path),
                    'active': False
                }
                
                # Add to our file list using the session state manager
                add_uploaded_file(file_info)
            
            # Update the set of processed files
            st.session_state.last_processed_files = current_files
            
            # Rerun to update the UI
            st.rerun()
    
    # Get the current list of files
    files = get_uploaded_files()
    
    # Display uploaded files with reordering controls
    if files:
        st.markdown("### Your Files")
        
        for i, file_info in enumerate(files):
            # Create columns for file name, move buttons, download, and delete button
            cols = st.columns([4, 1, 1, 1, 1])
            
            # File name with active state
            with cols[0]:
                if st.button(
                    f"📄 {file_info['name']}",
                    key=f"select_{i}",
                    use_container_width=True,
                    type="primary" if file_info.get('active') else "secondary"
                ):
                    # Set this file as active
                    set_active_file(file_info['path'])
                    st.rerun()
            
            # Move up button
            with cols[1]:
                if i > 0 and st.button("⬆️", key=f"up_{i}", help="Move up"):
                    # Swap with previous file
                    files[i], files[i-1] = files[i-1], files[i]
                    # Update active file if needed
                    if file_info.get('active') and i > 0:
                        set_active_file(files[i-1]['path'])
                    st.rerun()
            
            # Move down button
            with cols[2]:
                if i < len(files) - 1 and st.button("⬇️", key=f"down_{i}", help="Move down"):
                    # Swap with next file
                    files[i], files[i+1] = files[i+1], files[i]
                    # Update active file if needed
                    if file_info.get('active') and i < len(files) - 1:
                        set_active_file(files[i+1]['path'])
                    st.rerun()
            
            # Download button
            with cols[3]:
                file_path = Path(file_info['path'])
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    st.download_button(
                        label="📥",
                        data=file_data,
                        file_name=file_info['name'],
                        mime=f"audio/{file_path.suffix[1:]}",
                        key=f"download_{i}",
                        help="Download file"
                    )
            
            # Delete button
            with cols[4]:
                if st.button("❌", key=f"delete_{i}", help="Remove file"):
                    try:
                        file_path = Path(file_info['path'])
                        
                        # Remove the file using the session state manager
                        remove_uploaded_file(file_info['path'])
                        
                        # Remove the file from the filesystem if it exists
                        if file_path.exists():
                            try:
                                file_path.unlink()
                            except Exception as e:
                                st.error(f"Could not delete file: {e}")
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
                        import traceback
                        st.error(traceback.format_exc())
    else:
        st.info("No files uploaded yet. Use the uploader above to add files.")
        
    # Add a clear all button at the bottom
    if files and st.button("🗑️ Clear All Files", use_container_width=True):
        # Remove all files from the filesystem
        for file_info in files:
            file_path = Path(file_info['path'])
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception as e:
                    st.error(f"Could not delete file {file_info['name']}: {e}")
        
        # Clear the session state
        st.session_state.uploaded_files = []
        st.session_state.active_file = None
        st.rerun()

def render_main_content() -> None:
    """Render the main content area."""
    # Main content area
    st.title(f"{APP_NAME} {VERSION}")
    
    # Display the selected module or welcome message
    if st.session_state.get("selected_module") in MODULES:
        module_class = MODULES[st.session_state.get("selected_module")]
        module = module_class()
        module.render_ui()
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to the Audio Processing Dashboard! 👋
        
        Get started by:
        1. Uploading an audio file using the file manager on the right
        2. Selecting a processing module from the left sidebar
        3. Configuring the module's settings and applying the effects
        
        ### Available Modules
        """)
        
        # List available modules
        for module_name, module_class in MODULES.items():
            module = module_class()
            st.markdown(f"- **{module_name}** {module.config.icon} - {module.config.description}")

def main() -> None:
    """Main application function."""
    # Initialize the app
    init()
    
    # Create the main layout with three columns
    left_col, main_col, right_col = st.columns([1.5, 5, 2])
    
    # Left sidebar (modules)
    with left_col:
        render_module_sidebar()
    
    # Main content area
    with main_col:
        render_main_content()
    
    # Right sidebar (files)
    with right_col:
        render_file_sidebar()

if __name__ == "__main__":
    main()
