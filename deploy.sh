#!/bin/bash

# Exit on error
set -e

# Set project directory
PROJECT_DIR="/opt/containers/FFmpegDashboard"
REPO_URL="https://github.com/kbstn/ffmpeg_dashboard.git"

# Create directory if it doesn't exist
echo "Creating project directory..."
sudo mkdir -p "$(dirname "$PROJECT_DIR")"

# Navigate to containers directory
cd "$(dirname "$PROJECT_DIR")"

# Remove existing directory if it exists
if [ -d "$PROJECT_DIR" ]; then
    echo "Removing existing project directory..."
    sudo rm -rf "$PROJECT_DIR"
fi

# Clone the repository
echo "Cloning repository..."
sudo git clone "$REPO_URL" "$PROJECT_DIR"

# Navigate to project directory
cd "$PROJECT_DIR"

# Copy example.env to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    sudo cp .env.example .env
    
    # Set default values from example.env
    DEFAULT_PORT=$(grep -E '^STREAMLIT_SERVER_PORT=' .env.example | cut -d '=' -f2- || echo "8508")
    DEFAULT_ADDRESS=$(grep -E '^STREAMLIT_SERVER_ADDRESS=' .env.example | cut -d '=' -f2- || echo "0.0.0.0")
    
    # Check if Traefik host is configured in example
    if grep -q '^TRAEFIK_HOST=' .env.example; then
        DEFAULT_TRAEFIK_HOST=$(grep -E '^TRAEFIK_HOST=' .env.example | cut -d '=' -f2- || echo "")
    else
        DEFAULT_TRAEFIK_HOST=""
    fi
    
    # Prompt user for values
    read -p "Enter Streamlit server port [$DEFAULT_PORT]: " PORT
    PORT=${PORT:-$DEFAULT_PORT}
    
    read -p "Enter Streamlit server address [$DEFAULT_ADDRESS]: " ADDRESS
    ADDRESS=${ADDRESS:-$DEFAULT_ADDRESS}
    
    # Only ask for Traefik host if it was in the example or we have a default
    if [ -n "$DEFAULT_TRAEFIK_HOST" ] || [ -n "$TRAEFIK_HOST" ]; then
        read -p "Enter Traefik host [$DEFAULT_TRAEFIK_HOST]: " TRAEFIK_HOST
        TRAEFIK_HOST=${TRAEFIK_HOST:-$DEFAULT_TRAEFIK_HOST}
    fi
    
    # Update .env file with user values
    sudo sh -c "cat > .env << EOL
# Application settings
STREAMLIT_SERVER_PORT=$PORT
STREAMLIT_SERVER_ADDRESS=$ADDRESS

# Optional: Uncomment and set if using Traefik
TRAEFIK_HOST=$TRAEFIK_HOST
EOL"
    
    echo ".env file has been configured with your settings."
else
    echo ".env file already exists. Using existing configuration."
fi

# Build and start the containers
echo "Starting Docker Compose..."
sudo docker-compose up -d --build

echo -e "\nContainer is starting up..."
echo "Streamlit dashboard will be available at http://localhost:${PORT:-8508}"

# Show logs
echo -e "\nShowing logs (press Ctrl+C to exit):"
sudo docker-compose logs -f
