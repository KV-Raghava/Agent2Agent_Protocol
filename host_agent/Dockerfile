# Host Agent Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all host agent files to current directory
COPY . .



EXPOSE 8083

# Run the host agent app
CMD ["python", "app.py"]