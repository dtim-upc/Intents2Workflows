# Use an official Python runtime as the base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire content of the 'backend' folder to /app inside the container
COPY . .

# Install the required dependencies for backend and modules
RUN pip install --upgrade pip && \
    pip install -r api/requirements.txt && \
    pip install -r modules/IntentSpecification2WorkflowGenerator/requirements.txt && \
    pip install -r modules/IntentAnticipation/requirements.txt

# Expose the necessary ports
EXPOSE 9001 9002 9003 9004

# Command to run the backend services
CMD ["bash", "-c", "\
  uvicorn /api/main:app --port=9001 & \
  flask --app modules/IntentSpecification2WorkflowGenerator/api/api_main.py run --port=9002 & \
  python modules/IntentAnticipation/start_apis.py && \
  wait"]
