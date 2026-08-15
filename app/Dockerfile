# Production Dockerfile for IERL FastAPI Backend Engine
FROM python:3.11-slim

WORKDIR /opt/ierl

# Prevent Python from writing bytecode and buffer stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Build this image from the repository root:
# docker build -f app/Dockerfile -t ierl-equity-os .
# Install backend dependencies.
COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend package and the separately served frontend assets.
COPY app ./app
COPY frontend_deploy ./frontend_deploy

# Expose FastAPI default port
EXPOSE 8000

# Start production uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
