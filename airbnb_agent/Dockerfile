# Airbnb Agent Dockerfile
FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all weather agent files to current directory
COPY . .

EXPOSE 10002

# Run the module (since we're in /app and weather_agent is a package)

CMD ["python", "__main__.py"]