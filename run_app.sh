#!/bin/bash
# Run the Audio Processing Dashboard

# Activate the micromamba environment
micromamba activate audio_dashboard

# Set the PYTHONPATH to include the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the app using the -m flag to handle imports correctly
python -m streamlit run app/main.py