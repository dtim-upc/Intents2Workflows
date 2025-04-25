# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install necessary packages
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the code
COPY . .

# Expose the ports of the two APIs
EXPOSE 9003 9004

# Run a script to load data into GraphDB and then start the APIs
CMD ["sh", "-c", "python start_apis.py"]