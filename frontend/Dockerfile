# Use the Node alpine official image
FROM node:lts-alpine as build

# Create and change to the app directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application code
COPY . ./

# Build the app
RUN npm run build

# Use Nginx to serve the static files
FROM nginx:alpine

# Copy the build output to replace the default nginx contents
COPY --from=build /app/dist/marketplace /usr/share/nginx/html

# Setup nginx configuration for Angular routing with IPv6 support and health check
RUN echo 'server { \
    listen 80; \
    listen [::]:80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    # Health check endpoint for Railway \
    location = /health { \
        access_log off; \
        add_header Content-Type text/plain; \
        return 200 "healthy\n"; \
    } \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]