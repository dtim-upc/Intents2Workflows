# Use an official Node.js runtime as the base image
FROM node:18.20.6

# Set the working directory in the container to /app/frontend
WORKDIR /app

# Install global dependencies for Yarn and Quasar CLI
# RUN npm install -g yarn
RUN npm install -g @quasar/cli

# Copy only the frontend directory content to /app/frontend inside the container
COPY . .

# # Remove any existing node_modules to avoid platform-specific binaries
# RUN rm -rf /node_modules

# # Install frontend dependencies
RUN npm install --force
RUN yarn install

# Expose the necessary port for the frontend
EXPOSE 9000

# Command to run the frontend using Quasar
CMD ["quasar", "dev"]