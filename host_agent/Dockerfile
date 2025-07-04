# Host Agent Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all host agent files to current directory
COPY . .

EXPOSE 8083

# Default to API app, but can be overridden
# Use API_MODE environment variable to switch between gradio and api
ENV API_MODE=api

# Run the appropriate app based on API_MODE
CMD if [ "$API_MODE" = "gradio" ]; then python app.py; else python api_app.py; fi