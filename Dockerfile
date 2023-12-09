# Use the official Ubuntu image as the base image
FROM ubuntu:20.04

# Install required dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnotify-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the script and other necessary files into the container
COPY . /app/

# Install dependencies from requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Set environment variables
ENV DISPLAY=:0

# Run the script when the container launches
CMD ["python3", "password-manager.py"]
