"""
UI Utilities

This module provides common UI components used across the application.
"""
from typing import List, Dict, Any, Optional, Union
import streamlit as st


def select_files(
    label: str,
    key: str,
    multiple: bool = True,
    file_types: Optional[List[str]] = None,
    session_state_key: str = "uploaded_files"
) -> List[Dict[str, Any]]:
    """
    Unified file selection component.
    
    Args:
        label: Label for the select widget
        key: Unique key for the widget
        multiple: Whether to allow multiple file selection
        file_types: List of allowed file extensions (e.g., ['.mp3', '.wav'])
        session_state_key: Key in st.session_state containing file list
        
    Returns:
        List of selected file dictionaries with 'name' and 'path' keys
    """
    files = st.session_state.get(session_state_key, [])
    
    if not files:
        st.warning("No files available. Please upload files in the File Manager.")
        return []
    
    # Filter by file type if specified
    if file_types:
        files = [
            f for f in files 
            if any(f['name'].lower().endswith(ext.lower()) for ext in file_types)
        ]
        if not files:
            st.warning(f"No files with supported formats: {', '.join(file_types)}")
            return []
    
    file_names = [f["name"] for f in files]
    
    if multiple:
        selected_indices = st.multiselect(
            label,
            range(len(files)),
            format_func=lambda i: file_names[i],
            key=f"file_select_{key}"
        )
    else:
        selected_index = st.selectbox(
            label,
            range(len(files)),
            format_func=lambda i: file_names[i],
            key=f"file_select_{key}",
            index=0
        )
        selected_indices = [selected_index] if selected_index is not None else []
    
    return [files[i] for i in selected_indices]
