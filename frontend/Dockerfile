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

# Create a script to inject environment variables into the app
RUN echo '#!/bin/sh\n\
# Inject environment variables into the app at runtime\n\
cat > /usr/share/nginx/html/env-config.js << EOF\n\
window.ENV = {\n\
  BACKEND_URL: "$BACKEND_URL"\n\
};\n\
EOF\n\
\n\
# Start nginx\n\
exec nginx -g "daemon off;"\n\
' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

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

# Add script to inject the env-config.js reference to index.html
RUN echo 'sed -i "s/<head>/<head><script src=\\"env-config.js\\"><\\/script>/" /usr/share/nginx/html/index.html' >> /docker-entrypoint.sh

# Expose port 80
EXPOSE 80

CMD ["/docker-entrypoint.sh"]