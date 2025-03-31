# This is a proxy Dockerfile that pulls in the real frontend Dockerfile
FROM gcr.io/docker-pull-through/library/node:lts-alpine

WORKDIR /app

# Copy the frontend files
COPY frontend/ ./

# Install dependencies
RUN npm ci

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Expose port 80
EXPOSE 80

# Start the Angular dev server
CMD ["npm", "start", "--", "--port", "80"]