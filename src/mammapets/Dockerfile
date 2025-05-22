FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential default-libmysqlclient-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create config directory in the image
RUN mkdir /config

# Add requirements.pip from project root's config to /config/ in image
# Path is relative to the new Dockerfile location (src/mammapets/)
ADD ../../config/requirements.pip /config/requirements.pip

# Install Python dependencies
RUN pip install --no-cache-dir -r /config/requirements.pip

# Create app directory and set as working directory
RUN mkdir /app
WORKDIR /app

# Copy application code from the build context (src/mammapets/) into /app in the image
COPY . /app/
