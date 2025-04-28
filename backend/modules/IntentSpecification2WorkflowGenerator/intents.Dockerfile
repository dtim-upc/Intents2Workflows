# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Expose the application's port (default for FastAPI is 8000)
EXPOSE 9002

# Run API
CMD ["flask", "--app", "./api/api_main.py", "run", "--host", "0.0.0.0", "--port", "9002" ]
