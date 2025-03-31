FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Install Angular CLI globally
RUN npm install -g @angular/cli@19.2.0

# Copy the rest of the application
COPY . .

# Expose port 80 (will be overridden by PORT env var if set)
EXPOSE 80

# Start using npm start which runs ng serve with proper options
CMD ["npm", "start"]