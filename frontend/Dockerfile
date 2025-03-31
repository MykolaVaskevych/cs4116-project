FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Expose port 80
EXPOSE 80

# Start the Angular dev server
CMD ["npm", "start", "--", "--port", "80"]