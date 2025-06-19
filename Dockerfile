# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV STREAMLIT_SERVER_PORT=${STREAMLIT_SERVER_PORT:-8508}
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PYTHONPATH=/app

# Expose the port
EXPOSE ${STREAMLIT_SERVER_PORT}

# Command to run the application
CMD ["sh", "-c", "streamlit run /app/app/main.py --server.port=${STREAMLIT_SERVER_PORT} --server.address=0.0.0.0 --server.headless=true --server.enableCORS=false --server.enableXsrfProtection=false"]