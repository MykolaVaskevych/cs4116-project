# Use Node.js as base
FROM node:lts-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Install Angular CLI globally
RUN npm install -g @angular/cli

# Copy the rest of the application code
COPY . .

# Expose port 80
EXPOSE 80

# Start the Angular dev server
CMD ["npm", "start", "--", "--port", "80"]