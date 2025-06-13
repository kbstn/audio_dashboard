#!/bin/bash
# Setup script for Audio Processing Dashboard

echo "🚀 Setting up Audio Processing Dashboard development environment..."

# Check if micromamba is installed
if ! command -v micromamba &> /dev/null; then
    echo "❌ micromamba is not installed. Please install it first."
    echo "   Visit: https://mamba.readthedocs.io/en/latest/installation.html"
    exit 1
fi

# Create and activate environment
echo "🔧 Creating micromamba environment..."
micromamba create -n audio_dashboard -f environment.yml -y

# Activate the environment
echo "✅ Environment created. Activating..."
micromamba activate audio_dashboard

# Create uploads directory if it doesn't exist
mkdir -p uploads

echo "✨ Setup complete!"
echo "To start the application, run:"
echo "   micromamba activate audio_dashboard"
echo "   streamlit run app/main.py"

# Make the script executable
chmod +x setup_environment.sh
