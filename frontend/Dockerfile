# Build stage
FROM node:lts-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy the build output
COPY --from=build /app/dist/marketplace /usr/share/nginx/html

# Create a default configuration file for Nginx
RUN echo 'server {\n\
    listen 80;\n\
    listen [::]:80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    # Health check endpoint\n\
    location = /health {\n\
        access_log off;\n\
        add_header Content-Type text/plain;\n\
        return 200 "healthy\\n";\n\
    }\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Create environment variables injection script
RUN echo '#!/bin/sh\n\
# Create runtime environment config\n\
cat > /usr/share/nginx/html/env-config.js << EOF\n\
window.ENV = {\n\
  BACKEND_URL: "${BACKEND_URL:-https://backend.railway.app}"\n\
};\n\
EOF\n\
\n\
# Inject script reference into index.html\n\
sed -i "s/<head>/<head><script src=\\"env-config.js\\"><\\/script>/" /usr/share/nginx/html/index.html\n\
\n\
# Start nginx\n\
exec nginx -g "daemon off;"\n\
' > /docker-entrypoint.sh

RUN chmod +x /docker-entrypoint.sh

EXPOSE 80

CMD ["/docker-entrypoint.sh"]