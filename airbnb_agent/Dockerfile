# Airbnb Agent Dockerfile
FROM python:3.13-slim

# Install Node.js 20.x (LTS) to meet the engine requirements
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all weather agent files to current directory
COPY . .

EXPOSE 10002

# Run the module (since we're in /app and weather_agent is a package)
# CMD ["python", "__main__.py"]
CMD ["python", "-X", "tracemalloc", "__main__.py"]