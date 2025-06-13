"""
Session state management for the Audio Processing Dashboard.

This module provides utilities for managing the application's session state.
"""

import streamlit as st
from typing import Dict, Any, Optional, List

def init_session_state() -> None:
    """Initialize the application's session state with default values."""
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    if 'active_file' not in st.session_state:
        st.session_state.active_file = None

def get_uploaded_files() -> List[Dict[str, Any]]:
    """Get all uploaded files."""
    return st.session_state.get('uploaded_files', [])

def set_active_file(file_path: str) -> None:
    """Set the active file."""
    # First, clear active state from all files
    for file_info in st.session_state.get('uploaded_files', []):
        file_info['active'] = False
    
    # Set the new active file
    st.session_state.active_file = file_path
    
    # Update the active state in the file list
    for file_info in st.session_state.get('uploaded_files', []):
        if file_info['path'] == file_path:
            file_info['active'] = True
            break

def get_active_file() -> Optional[str]:
    """Get the currently active file path."""
    return st.session_state.get('active_file')

def add_uploaded_file(file_info: Dict[str, Any]) -> None:
    """
    Add a new uploaded file to the session state.
    
    Args:
        file_info: Dictionary containing 'name' and 'path' of the file
    """
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Ensure the file doesn't already exist
    if not any(f['path'] == file_info['path'] for f in st.session_state.uploaded_files):
        # Add to the beginning of the list
        st.session_state.uploaded_files.insert(0, file_info)
        set_active_file(file_info['path'])

def remove_uploaded_file(file_path: str) -> None:
    """
    Remove an uploaded file from the session state.
    
    Args:
        file_path: Path of the file to remove
    """
    if 'uploaded_files' in st.session_state:
        # Find and remove the file
        for i, file_info in enumerate(st.session_state.uploaded_files):
            if file_info['path'] == file_path:
                # If this was the active file, clear the active file
                if st.session_state.get('active_file') == file_path:
                    st.session_state.active_file = None
                    # Set another file as active if available
                    if st.session_state.uploaded_files:
                        next_file = st.session_state.uploaded_files[0]['path'] if i == 0 else st.session_state.uploaded_files[i-1]['path']
                        set_active_file(next_file)
                
                # Remove the file from the list
                st.session_state.uploaded_files.pop(i)
                break
