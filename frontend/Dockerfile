# Simple Dockerfile for Angular app
FROM node:lts-alpine

WORKDIR /app

# Copy all files from the current directory (frontend)
COPY . .

# Install dependencies
RUN npm ci

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Expose port 80
EXPOSE 80

# Start the Angular dev server
CMD ["npm", "start", "--", "--port", "80"]
