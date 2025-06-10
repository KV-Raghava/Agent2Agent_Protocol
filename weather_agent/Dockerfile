# Weather Agent Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all weather agent files to current directory
COPY . .

EXPOSE 10001

# Run the module (since we're in /app and weather_agent is a package)
# CMD ["python", "-m", "weather_agent"]
CMD ["python", "__main__.py"]